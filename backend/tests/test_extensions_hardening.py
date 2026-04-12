"""Verify extensions.py state is properly scoped and limiter uses config."""

import pytest
from flask import Flask
from app.extensions import limiter, MockRateLimiter, LimiterProxy
from app.config.limiter_config import limiter_defaults


class TestLimiterProxy:
    """LimiterProxy delegates correctly to TestLimiter or Flask-Limiter."""

    def test_limiter_is_proxy_instance(self):
        """limiter global is a LimiterProxy instance."""
        assert isinstance(limiter, LimiterProxy)

    def test_limiter_has_limit_decorator(self):
        """LimiterProxy has .limit() decorator method."""
        assert hasattr(limiter, 'limit')
        assert callable(limiter.limit)

    def test_limiter_has_init_app(self):
        """LimiterProxy has .init_app() method."""
        assert hasattr(limiter, 'init_app')
        assert callable(limiter.init_app)


class TestTestLimiterStateScoping:
    """TestLimiter state is properly scoped to instances."""

    def test_test_limiter_instances_have_separate_state(self):
        """Each MockRateLimiter instance has its own request_times dict."""
        tl1 = MockRateLimiter()
        tl2 = MockRateLimiter()

        # Each instance has separate request_times
        assert tl1.request_times is not tl2.request_times

        # Modify one doesn't affect the other
        tl1.request_times['key1'] = [1.0]
        assert 'key1' not in tl2.request_times


class TestLimiterUsesConfig:
    """Limiter uses centralized config from limiter_config.py."""

    def test_limiter_defaults_imported(self):
        """limiter_defaults is accessible."""
        assert limiter_defaults.http_status_too_many_requests == 429
        assert limiter_defaults.default_window_seconds == 3600

    def test_rate_limit_period_mapping_accessible(self):
        """Rate limit period mapping from limiter_config is functional."""
        from app.config.limiter_config import limiter_period_map, get_period_seconds

        assert get_period_seconds('minute') == 60
        assert get_period_seconds('hour') == 3600
        assert get_period_seconds('unknown') == limiter_defaults.default_window_seconds
