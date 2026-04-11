"""Verify limiter configuration is immutable and well-formed."""

import pytest
from app.config.limiter_config import (
    limiter_period_map, limiter_defaults, get_period_seconds
)


class TestLimiterConfigFrozen:
    """Limiter config dataclasses are frozen."""

    def test_limiter_defaults_frozen(self):
        """Attempt to mutate limiter_defaults raises FrozenInstanceError."""
        with pytest.raises(Exception):  # FrozenInstanceError
            limiter_defaults.default_window_seconds = 7200

    def test_limiter_period_map_frozen(self):
        """Attempt to mutate limiter_period_map raises FrozenInstanceError."""
        with pytest.raises(Exception):
            limiter_period_map.period_to_seconds = {}


class TestLimiterPeriodMapping:
    """Period string → seconds mapping is correct."""

    def test_all_periods_present(self):
        """All standard periods are mapped."""
        expected_periods = {'second', 'minute', 'hour', 'day'}
        assert expected_periods == set(limiter_period_map.period_to_seconds.keys())

    def test_period_values_correct(self):
        """Period values match standard definitions."""
        assert limiter_period_map.period_to_seconds['second'] == 1
        assert limiter_period_map.period_to_seconds['minute'] == 60
        assert limiter_period_map.period_to_seconds['hour'] == 3600
        assert limiter_period_map.period_to_seconds['day'] == 86400

    def test_get_period_seconds_known(self):
        """get_period_seconds returns correct value for known periods."""
        assert get_period_seconds('second') == 1
        assert get_period_seconds('minute') == 60
        assert get_period_seconds('hour') == 3600
        assert get_period_seconds('day') == 86400

    def test_get_period_seconds_unknown_uses_default(self):
        """get_period_seconds falls back to default for unknown period."""
        assert get_period_seconds('unknown') == limiter_defaults.default_window_seconds
        assert get_period_seconds('unknown', default=1800) == 1800


class TestLimiterDefaults:
    """Limiter defaults are valid."""

    def test_default_window_positive(self):
        """Default window is a positive integer."""
        assert limiter_defaults.default_window_seconds > 0

    def test_http_429_is_too_many_requests(self):
        """HTTP 429 is the correct status for too many requests."""
        assert limiter_defaults.http_status_too_many_requests == 429
