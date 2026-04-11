"""Verify route constants are immutable frozen dataclasses."""

import pytest
from app.config.route_constants import (
    route_auth_config, route_session_config, route_site_config,
    route_user_config, route_pagination_config, route_status_codes,
)


class TestRouteConstantsAreFrozen:
    """Frozen dataclasses prevent accidental mutation at runtime."""

    def test_auth_config_frozen(self):
        """Attempt to mutate route_auth_config raises FrozenInstanceError."""
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            route_auth_config.constant_time_delay_seconds = 1.0

    def test_session_config_frozen(self):
        """Attempt to mutate route_session_config raises FrozenInstanceError."""
        with pytest.raises(Exception):
            route_session_config.play_operator_diag_max = 100

    def test_site_config_frozen(self):
        """Attempt to mutate route_site_config raises FrozenInstanceError."""
        with pytest.raises(Exception):
            route_site_config.default_rotation_interval = 120

    def test_user_config_frozen(self):
        """Attempt to mutate route_user_config raises FrozenInstanceError."""
        with pytest.raises(Exception):
            route_user_config.role_level_max = 10000

    def test_pagination_config_frozen(self):
        """Attempt to mutate route_pagination_config raises FrozenInstanceError."""
        with pytest.raises(Exception):
            route_pagination_config.page_size_large = 200

    def test_status_codes_frozen(self):
        """Attempt to mutate route_status_codes raises FrozenInstanceError."""
        with pytest.raises(Exception):
            route_status_codes.ok = 201


class TestRouteConstantsValues:
    """Verify configured values match expected semantics."""

    def test_auth_config_timing_reasonable(self):
        """Auth delay is between 0.1 and 2 seconds."""
        assert 0.1 <= route_auth_config.constant_time_delay_seconds <= 2.0

    def test_session_diag_max_positive(self):
        """Diagnostic max is a reasonable positive integer."""
        assert route_session_config.play_operator_diag_max > 0

    def test_site_rotation_bounds_valid(self):
        """Rotation intervals are positive and min <= default <= max."""
        assert route_site_config.min_rotation_interval > 0
        assert route_site_config.default_rotation_interval > 0
        assert route_site_config.max_rotation_interval > 0
        assert (route_site_config.min_rotation_interval <=
                route_site_config.default_rotation_interval <=
                route_site_config.max_rotation_interval)

    def test_user_role_bounds_valid(self):
        """Role levels are non-negative and min <= max."""
        assert route_user_config.role_level_min >= 0
        assert route_user_config.role_level_max > 0
        assert route_user_config.role_level_min <= route_user_config.role_level_max

    def test_pagination_sizes_ordered(self):
        """Pagination sizes are positive and ordered."""
        sizes = [
            route_pagination_config.page_size_small,
            route_pagination_config.page_size_medium,
            route_pagination_config.page_size_large,
            route_pagination_config.page_size_max,
        ]
        assert all(s > 0 for s in sizes)
        assert all(sizes[i] <= sizes[i+1] for i in range(len(sizes)-1))

    def test_status_codes_standard_http(self):
        """Status codes are valid HTTP status values."""
        codes = [
            route_status_codes.ok, route_status_codes.created,
            route_status_codes.bad_request, route_status_codes.unauthorized,
            route_status_codes.forbidden, route_status_codes.not_found,
            route_status_codes.conflict, route_status_codes.internal_error,
            route_status_codes.too_many_requests,
        ]
        assert all(100 <= code < 600 for code in codes)
