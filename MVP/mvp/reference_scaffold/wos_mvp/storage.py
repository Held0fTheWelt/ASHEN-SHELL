"""SQLite persistence for the runnable MVP service."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
# UTC compatibility for Python 3.10
UTC = timezone.utc
from pathlib import Path
from typing import Any, Iterator

from .config import get_settings
from .incidents import IncidentRecord
from .logging_utils import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class StoredSession:
    session_id: str
    module_id: str
    artifact_id: str
    artifact_revision: str
    start_scene_id: str
    status: str
    current_turn: int
    transcript: list[dict[str, Any]]
    created_at: str
    updated_at: str


class SessionStore:
    """Incident-visible SQLite-backed session store."""

    def __init__(self, database_path: Path | None = None):
        settings = get_settings()
        self.database_path = Path(database_path or settings.database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            conn = self._connect()
            try:
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _init_db(self) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    module_id TEXT NOT NULL,
                    artifact_id TEXT NOT NULL,
                    artifact_revision TEXT NOT NULL,
                    start_scene_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_turn INTEGER NOT NULL,
                    transcript_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS event_logs (
                    event_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    turn_number INTEGER,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    incident_code TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def create_session(
        self,
        *,
        module_id: str,
        artifact_id: str,
        artifact_revision: str,
        start_scene_id: str,
        opening_text: str,
    ) -> StoredSession:
        now = datetime.now(UTC).isoformat()
        session_id = str(uuid.uuid4())
        transcript = [{"speaker": "gm", "text": opening_text, "turn": 0}]
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    session_id, module_id, artifact_id, artifact_revision, start_scene_id,
                    status, current_turn, transcript_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    module_id,
                    artifact_id,
                    artifact_revision,
                    start_scene_id,
                    "active",
                    0,
                    json.dumps(transcript),
                    now,
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO event_logs (event_id, session_id, event_type, turn_number, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    session_id,
                    "session_created",
                    0,
                    json.dumps({
                        "opening_text": opening_text,
                        "module_id": module_id,
                        "artifact_id": artifact_id,
                        "artifact_revision": artifact_revision,
                    }),
                    now,
                ),
            )
        logger.info("session_created", extra={"session_id": session_id, "event_type": "session_created"})
        return self.get_session(session_id)  # type: ignore[return-value]

    def get_session(self, session_id: str) -> StoredSession | None:
        with self._tx() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_session(row)

    def append_turn(
        self,
        *,
        session_id: str,
        player_input: str,
        gm_output: str,
        turn_number: int,
        strategy: str,
        support_action: str,
        retrieved_memory_ids: list[str],
    ) -> StoredSession:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError(session_id)
        transcript = list(session.transcript)
        transcript.append({"speaker": "player", "text": player_input, "turn": turn_number})
        transcript.append({"speaker": "gm", "text": gm_output, "turn": turn_number})
        updated_at = datetime.now(UTC).isoformat()
        payload = {
            "player_input": player_input,
            "gm_output": gm_output,
            "strategy": strategy,
            "support_action": support_action,
            "retrieved_memory_ids": retrieved_memory_ids,
        }
        with self._tx() as conn:
            conn.execute(
                """
                UPDATE sessions
                SET current_turn = ?, transcript_json = ?, updated_at = ?
                WHERE session_id = ?
                """,
                (turn_number, json.dumps(transcript), updated_at, session_id),
            )
            conn.execute(
                """
                INSERT INTO event_logs (event_id, session_id, event_type, turn_number, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    session_id,
                    "turn_committed",
                    turn_number,
                    json.dumps(payload),
                    updated_at,
                ),
            )
        logger.info("turn_committed", extra={"session_id": session_id, "event_type": "turn_committed"})
        return self.get_session(session_id)  # type: ignore[return-value]

    def get_logs(self, session_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
        with self._tx() as conn:
            rows = conn.execute(
                """
                SELECT event_type, turn_number, payload_json, created_at
                FROM event_logs
                WHERE session_id = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        return [
            {
                "event_type": row["event_type"],
                "turn_number": row["turn_number"],
                "payload": json.loads(row["payload_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def record_incident(self, incident: IncidentRecord) -> dict[str, Any]:
        created_at = datetime.now(UTC).isoformat()
        data = {
            "incident_id": str(uuid.uuid4()),
            "session_id": incident.session_id,
            "incident_code": incident.incident_code,
            "severity": incident.severity,
            "message": incident.message,
            "details_json": json.dumps(incident.details),
            "created_at": created_at,
        }
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO incidents (
                    incident_id, session_id, incident_code, severity, message, details_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["incident_id"],
                    data["session_id"],
                    data["incident_code"],
                    data["severity"],
                    data["message"],
                    data["details_json"],
                    data["created_at"],
                ),
            )
        logger.warning(
            incident.message,
            extra={"session_id": incident.session_id, "event_type": incident.incident_code},
        )
        return data

    def get_incidents(self, session_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM incidents"
        params: tuple[Any, ...] = ()
        if session_id is not None:
            query += " WHERE session_id = ?"
            params = (session_id,)
        query += " ORDER BY created_at ASC"
        with self._tx() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "incident_id": row["incident_id"],
                "session_id": row["session_id"],
                "incident_code": row["incident_code"],
                "severity": row["severity"],
                "message": row["message"],
                "details": json.loads(row["details_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def _row_to_session(self, row: sqlite3.Row) -> StoredSession:
        return StoredSession(
            session_id=row["session_id"],
            module_id=row["module_id"],
            artifact_id=row["artifact_id"],
            artifact_revision=row["artifact_revision"],
            start_scene_id=row["start_scene_id"],
            status=row["status"],
            current_turn=int(row["current_turn"]),
            transcript=json.loads(row["transcript_json"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
