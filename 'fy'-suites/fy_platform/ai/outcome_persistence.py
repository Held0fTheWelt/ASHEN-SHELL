"""OutcomePersistence: Store and retrieve composition outcomes for cross-session learning."""

from __future__ import annotations

import sqlite3
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class CompositionOutcome:
    """Record of a composition run outcome."""
    composition_id: str
    suites: list[str]
    predicted_cost: float
    actual_cost: float
    fixtures_used: list[str] = field(default_factory=list)
    outcome_status: str = 'success'  # 'success', 'partial', 'failed'
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dict for serialization."""
        return {
            'composition_id': self.composition_id,
            'suites': self.suites,
            'predicted_cost': self.predicted_cost,
            'actual_cost': self.actual_cost,
            'fixtures_used': self.fixtures_used,
            'outcome_status': self.outcome_status,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
        }


class OutcomePersistence:
    """Store and retrieve composition outcomes in SQLite database.

    Enables 5+ years of outcome history (∼7,000-10,000 compositions/year).
    Schema: id, suites, predicted_cost, actual_cost, fixtures_used, outcome_status, timestamp

    Features:
    - Database connection retry logic (3 retries, exponential backoff)
    - Outcome deduplication (prevent storing same composition twice)
    """

    def __init__(self, db_path: str | Path = None, max_retries: int = 3):
        """Initialize outcome persistence.

        Parameters
        ----------
        db_path : str | Path, optional
            Path to SQLite database. Defaults to 'fy'-suites/data/outcomes.db
        max_retries : int, optional
            Maximum database connection retries. Default 3.
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / 'data' / 'outcomes.db'

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self._initialize_schema()

    def _initialize_schema(self):
        """Initialize SQLite schema if not exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    composition_id TEXT UNIQUE NOT NULL,
                    suites TEXT NOT NULL,
                    predicted_cost REAL NOT NULL,
                    actual_cost REAL NOT NULL,
                    fixtures_used TEXT,
                    outcome_status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON outcomes(timestamp)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_status ON outcomes(outcome_status)
            ''')
            conn.commit()

    def store_outcome(self, outcome: CompositionOutcome, check_duplicate: bool = True) -> str:
        """Store a composition outcome with retry logic and deduplication.

        Parameters
        ----------
        outcome : CompositionOutcome
            Outcome to store
        check_duplicate : bool, optional
            Check for duplicate outcome before storing. Default True.

        Returns
        -------
        str
            Composition ID
        """
        # Check for duplicate if enabled
        if check_duplicate and self.check_duplicate_outcome(outcome):
            return outcome.composition_id

        # Store with retry logic
        return self.retry_on_db_error(
            self._store_outcome_unsafe, outcome
        )

    def _store_outcome_unsafe(self, outcome: CompositionOutcome) -> str:
        """Internal unsafe store (no retries).

        Parameters
        ----------
        outcome : CompositionOutcome
            Outcome to store

        Returns
        -------
        str
            Composition ID
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO outcomes
                (composition_id, suites, predicted_cost, actual_cost,
                 fixtures_used, outcome_status, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                outcome.composition_id,
                json.dumps(outcome.suites),
                outcome.predicted_cost,
                outcome.actual_cost,
                json.dumps(outcome.fixtures_used),
                outcome.outcome_status,
                outcome.timestamp,
                json.dumps(outcome.metadata),
            ))
            conn.commit()
        return outcome.composition_id

    def load_outcome(self, composition_id: str) -> CompositionOutcome | None:
        """Load a specific outcome by composition ID.

        Parameters
        ----------
        composition_id : str
            Composition ID to load

        Returns
        -------
        CompositionOutcome | None
            Loaded outcome or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT composition_id, suites, predicted_cost, actual_cost,
                       fixtures_used, outcome_status, timestamp, metadata
                FROM outcomes WHERE composition_id = ?
            ''', (composition_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return CompositionOutcome(
            composition_id=row[0],
            suites=json.loads(row[1]),
            predicted_cost=row[2],
            actual_cost=row[3],
            fixtures_used=json.loads(row[4]) if row[4] else [],
            outcome_status=row[5],
            timestamp=row[6],
            metadata=json.loads(row[7]) if row[7] else {},
        )

    def load_outcomes(self, status: str | None = None, limit: int = 1000) -> list[CompositionOutcome]:
        """Load all outcomes, optionally filtered by status.

        Parameters
        ----------
        status : str, optional
            Filter by outcome status ('success', 'partial', 'failed')
        limit : int, optional
            Maximum results to return. Default 1000.

        Returns
        -------
        list[CompositionOutcome]
            List of outcomes
        """
        with sqlite3.connect(self.db_path) as conn:
            if status:
                cursor = conn.execute('''
                    SELECT composition_id, suites, predicted_cost, actual_cost,
                           fixtures_used, outcome_status, timestamp, metadata
                    FROM outcomes WHERE outcome_status = ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (status, limit))
            else:
                cursor = conn.execute('''
                    SELECT composition_id, suites, predicted_cost, actual_cost,
                           fixtures_used, outcome_status, timestamp, metadata
                    FROM outcomes ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
            rows = cursor.fetchall()

        outcomes = []
        for row in rows:
            outcomes.append(CompositionOutcome(
                composition_id=row[0],
                suites=json.loads(row[1]),
                predicted_cost=row[2],
                actual_cost=row[3],
                fixtures_used=json.loads(row[4]) if row[4] else [],
                outcome_status=row[5],
                timestamp=row[6],
                metadata=json.loads(row[7]) if row[7] else {},
            ))

        return outcomes

    def outcomes_for_composition(self, composition_id: str) -> list[CompositionOutcome]:
        """Load all outcomes for a specific composition.

        Parameters
        ----------
        composition_id : str
            Composition ID pattern (supports prefix matching)

        Returns
        -------
        list[CompositionOutcome]
            Matching outcomes
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT composition_id, suites, predicted_cost, actual_cost,
                       fixtures_used, outcome_status, timestamp, metadata
                FROM outcomes WHERE composition_id LIKE ?
                ORDER BY timestamp DESC
            ''', (f'{composition_id}%',))
            rows = cursor.fetchall()

        outcomes = []
        for row in rows:
            outcomes.append(CompositionOutcome(
                composition_id=row[0],
                suites=json.loads(row[1]),
                predicted_cost=row[2],
                actual_cost=row[3],
                fixtures_used=json.loads(row[4]) if row[4] else [],
                outcome_status=row[5],
                timestamp=row[6],
                metadata=json.loads(row[7]) if row[7] else {},
            ))

        return outcomes

    def outcomes_for_suite(self, suite: str, limit: int = 100) -> list[CompositionOutcome]:
        """Load outcomes for compositions including a specific suite.

        Parameters
        ----------
        suite : str
            Suite name to filter by
        limit : int, optional
            Maximum results. Default 100.

        Returns
        -------
        list[CompositionOutcome]
            Matching outcomes
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT composition_id, suites, predicted_cost, actual_cost,
                       fixtures_used, outcome_status, timestamp, metadata
                FROM outcomes ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()

        outcomes = []
        for row in rows:
            suites = json.loads(row[1])
            if suite in suites:
                outcomes.append(CompositionOutcome(
                    composition_id=row[0],
                    suites=suites,
                    predicted_cost=row[2],
                    actual_cost=row[3],
                    fixtures_used=json.loads(row[4]) if row[4] else [],
                    outcome_status=row[5],
                    timestamp=row[6],
                    metadata=json.loads(row[7]) if row[7] else {},
                ))

        return outcomes

    def outcome_count(self) -> int:
        """Get total number of stored outcomes.

        Returns
        -------
        int
            Total outcome count
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM outcomes')
            count = cursor.fetchone()[0]
        return count

    def outcome_count_by_status(self) -> dict[str, int]:
        """Get outcome counts grouped by status.

        Returns
        -------
        dict[str, int]
            Count by status ('success', 'partial', 'failed')
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT outcome_status, COUNT(*) as count
                FROM outcomes GROUP BY outcome_status
            ''')
            rows = cursor.fetchall()

        return {row[0]: row[1] for row in rows}

    def clear_outcomes(self) -> int:
        """Clear all outcomes from database.

        Returns
        -------
        int
            Number of outcomes deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM outcomes')
            count = cursor.rowcount
            conn.commit()
        return count

    def retry_on_db_error(self, func, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry on database error.

        Parameters
        ----------
        func : callable
            Function to execute
        *args
            Positional arguments for func
        **kwargs
            Keyword arguments for func

        Returns
        -------
        Any
            Return value from func

        Raises
        ------
        sqlite3.DatabaseError
            If all retries exhausted
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 0.1s, 0.2s, 0.4s
                    wait_time = (0.1 * (2 ** attempt))
                    time.sleep(wait_time)
                else:
                    break

        # All retries exhausted
        if last_error:
            raise last_error
        raise sqlite3.DatabaseError("Database operation failed")

    def check_duplicate_outcome(self, outcome: CompositionOutcome) -> bool:
        """Check if outcome with same composition exists.

        Prevents storing duplicate compositions (same suites, similar costs).

        Parameters
        ----------
        outcome : CompositionOutcome
            Outcome to check

        Returns
        -------
        bool
            True if duplicate found
        """
        try:
            existing = self.load_outcome(outcome.composition_id)
            if existing is None:
                return False

            # Check if it's truly a duplicate (same suites and similar costs)
            same_suites = set(existing.suites) == set(outcome.suites)
            cost_diff = abs(existing.actual_cost - outcome.actual_cost)
            similar_cost = cost_diff < 0.01  # Within 1 cent

            return same_suites and similar_cost
        except Exception:
            return False
