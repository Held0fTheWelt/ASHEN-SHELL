"""Rate limiter configuration: period mappings and defaults.

All mappings are frozen to prevent accidental drift during tests/runtime.
"""

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class LimiterPeriodMap:
    """Maps period strings (e.g., 'minute') to seconds."""
    period_to_seconds: Mapping[str, int] = None

    def __post_init__(self):
        # Bypass frozen to set the mapping (dict is immutable reference)
        object.__setattr__(self, 'period_to_seconds', {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        })


@dataclass(frozen=True)
class LimiterDefaults:
    """Rate limiter defaults for test and production modes."""
    default_window_seconds: int = 3600
    """Default rate limit window (1 hour) when period string is unrecognized."""
    http_status_too_many_requests: int = 429
    """HTTP status code for rate limit exceeded."""


# Singleton instances
limiter_period_map = LimiterPeriodMap()
limiter_defaults = LimiterDefaults()


def get_period_seconds(period_str: str, default: int = None) -> int:
    """Get seconds for a period string, with fallback to default.

    Args:
        period_str: Period string like 'minute', 'hour', 'day'.
        default: Fallback value if period_str not recognized.

    Returns:
        Seconds for the period, or default (or limiter_defaults.default_window_seconds).
    """
    if default is None:
        default = limiter_defaults.default_window_seconds
    return limiter_period_map.period_to_seconds.get(period_str, default)
