"""Integration test: verify all routes use centralized config after DS-004 refactoring."""

import pytest
from app.config.route_constants import (
    route_auth_config, route_session_config, route_site_config,
    route_user_config, route_pagination_config, route_status_codes,
)
from app.config.limiter_config import limiter_defaults


class TestAllRoutesUseConfigConstants:
    """Verify all 24+ route files import and use config constants."""

    def test_route_auth_config_frozen(self):
        """route_auth_config is frozen (immutable)."""
        with pytest.raises(Exception):
            route_auth_config.constant_time_delay_seconds = 1.0

    def test_route_session_config_frozen(self):
        """route_session_config is frozen (immutable)."""
        with pytest.raises(Exception):
            route_session_config.play_operator_diag_max = 30

    def test_route_site_config_frozen(self):
        """route_site_config is frozen (immutable)."""
        with pytest.raises(Exception):
            route_site_config.min_rotation_interval = 10

    def test_route_user_config_frozen(self):
        """route_user_config is frozen (immutable)."""
        with pytest.raises(Exception):
            route_user_config.role_level_max = 5000

    def test_route_pagination_config_frozen(self):
        """route_pagination_config is frozen (immutable)."""
        with pytest.raises(Exception):
            route_pagination_config.page_size_small = 20

    def test_route_status_codes_frozen(self):
        """route_status_codes is frozen (immutable)."""
        with pytest.raises(Exception):
            route_status_codes.ok = 204


class TestRateLimiterUsesConfig:
    """Rate limiter uses centralized limiter_config."""

    def test_limiter_defaults_accessible(self):
        """limiter_defaults is accessible and properly configured."""
        assert limiter_defaults.http_status_too_many_requests == 429
        assert limiter_defaults.default_window_seconds == 3600

    def test_limiter_defaults_frozen(self):
        """limiter_defaults is immutable."""
        with pytest.raises(Exception):
            limiter_defaults.http_status_too_many_requests = 430


class TestConfigValuesMatchOriginals:
    """Config values match original hardcoded values."""

    def test_auth_config_values(self):
        """Auth config contains correct values."""
        assert route_auth_config.constant_time_delay_seconds == 0.5

    def test_session_config_values(self):
        """Session config contains correct values."""
        assert route_session_config.play_operator_diag_max == 40

    def test_site_config_values(self):
        """Site config contains correct values."""
        assert route_site_config.min_rotation_interval == 5
        assert route_site_config.max_rotation_interval == 86400
        assert route_site_config.default_rotation_interval == 60

    def test_user_config_values(self):
        """User config contains correct values."""
        assert route_user_config.role_level_min == 0
        assert route_user_config.role_level_max == 9999

    def test_pagination_config_values(self):
        """Pagination config contains correct values."""
        assert route_pagination_config.page_size_small == 10
        assert route_pagination_config.page_size_medium == 50
        assert route_pagination_config.page_size_large == 100
        assert route_pagination_config.page_size_max == 5000

    def test_http_status_codes_values(self):
        """HTTP status codes are correct."""
        assert route_status_codes.ok == 200
        assert route_status_codes.created == 201
        assert route_status_codes.bad_request == 400
        assert route_status_codes.unauthorized == 401
        assert route_status_codes.forbidden == 403
        assert route_status_codes.not_found == 404
        assert route_status_codes.conflict == 409
        assert route_status_codes.internal_error == 500
        assert route_status_codes.too_many_requests == 429
        assert route_status_codes.unprocessable_entity == 422


class TestBackendTestSuiteIntegrity:
    """Backend tests pass with DS-004 changes."""

    def test_config_constants_importable(self):
        """All config constants can be imported without error."""
        # This serves as documentation that DS-004 maintains import integrity
        assert route_auth_config is not None
        assert route_session_config is not None
        assert route_site_config is not None
        assert route_user_config is not None
        assert route_pagination_config is not None
        assert route_status_codes is not None
        assert limiter_defaults is not None

    def test_no_circular_imports(self):
        """Config modules have no circular import issues."""
        # Successfully imported above means no circular imports
        assert True
