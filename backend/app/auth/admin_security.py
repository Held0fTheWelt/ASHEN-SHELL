"""
Multi-layer security decorator for admin endpoints.

Implements comprehensive security checks:
1. JWT and admin role verification
2. Role level verification (SuperAdmin for sensitive operations)
3. IP whitelist enforcement (if configured)
4. Per-admin rate limiting
5. 2FA verification for sensitive operations
6. Comprehensive audit logging
"""

import logging
from functools import wraps
from typing import Callable, Optional

from flask import current_app, g, jsonify, request
from flask_jwt_extended import jwt_required

from app.auth import admin_security_helpers
from app.auth.admin_security_helpers import _get_client_ip
from app.auth.admin_security_policy import AdminSecurityConfig, evaluate_admin_security_gate
from app.auth.permissions import get_current_user

logger = logging.getLogger(__name__)

_rate_limit_cache = admin_security_helpers._rate_limit_cache

# Re-export for tests and backwards compatibility
from app.auth.admin_security_helpers import (  # noqa: E402
    _check_rate_limit,
    _is_ip_whitelisted,
    _verify_2fa,
)

__all__ = [
    "AdminSecurityConfig",
    "admin_security",
    "admin_security_sensitive",
    "get_admin_security_context",
    "get_admin_security_user",
    "_check_rate_limit",
    "_get_client_ip",
    "_is_ip_whitelisted",
    "_rate_limit_cache",
    "_verify_2fa",
]


def _log_admin_action(
    user,
    action: str,
    resource: str,
    status: str = "success",
    details: Optional[dict] = None,
):
    """Log admin action to audit log."""
    from app.services import log_activity

    metadata = {
        "security_level": "admin",
        "resource": resource,
        **(details or {}),
    }

    log_activity(
        actor=user,
        category="admin_security",
        action=action,
        status=status,
        message=f"Admin action: {action} on {resource}",
        route=request.path,
        method=request.method,
        metadata=metadata,
        tags=["admin", "security"],
    )


def _log_security_violation(
    user,
    violation_type: str,
    reason: str,
    details: Optional[dict] = None,
):
    """Log security violation for alerting."""
    from app.services import log_activity

    metadata = {
        "violation_type": violation_type,
        "reason": reason,
        "client_ip": _get_client_ip(),
        **(details or {}),
    }

    log_activity(
        actor=user,
        category="security",
        action="admin_security_violation",
        status="critical",
        message=f"Admin security violation: {violation_type} - {reason}",
        route=request.path,
        method=request.method,
        metadata=metadata,
        tags=["admin", "security", "violation"],
    )

    logger.critical(
        "Admin security violation: %s",
        violation_type,
        extra={
            "event_type": "admin_security_violation",
            "violation_type": violation_type,
            "reason": reason,
            "user_id": user.id if user else None,
            "username": user.username if user else None,
            "client_ip": _get_client_ip(),
            **metadata,
        },
    )


def admin_security(
    require_2fa: bool = False,
    require_super_admin: bool = False,
    rate_limit: Optional[str] = None,
    audit_log: bool = True,
    check_ip_whitelist: bool = True,
) -> Callable:
    """Multi-layer security decorator for admin endpoints."""
    config = AdminSecurityConfig(
        require_2fa=require_2fa,
        require_super_admin=require_super_admin,
        rate_limit=rate_limit,
        audit_log=audit_log,
        check_ip_whitelist=check_ip_whitelist,
    )

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            denial = evaluate_admin_security_gate(
                user, config, client_ip=_get_client_ip()
            )
            if denial is not None:
                if denial.violation_type:
                    _log_security_violation(
                        user,
                        denial.violation_type,
                        denial.violation_reason,
                        denial.violation_details,
                    )
                return jsonify(denial.json_body), denial.http_status

            g.admin_security_user = user
            g.admin_security_config = config

            try:
                result = f(*args, **kwargs)

                if config.audit_log:
                    resource = f"{request.path}:{request.method}"
                    _log_admin_action(
                        user,
                        action=f.__name__,
                        resource=resource,
                        status="success",
                    )

                return result
            except Exception as e:
                _log_security_violation(
                    user,
                    "admin_operation_error",
                    f"Error during admin operation: {str(e)}",
                )
                logger.exception("Error in admin operation %s", f.__name__)
                raise

        wrapped = jwt_required()(wrapped)
        return wrapped

    return decorator


def admin_security_sensitive(
    operation_name: str = "sensitive_operation",
    require_super_admin: bool = True,
) -> Callable:
    """Convenience decorator for highly sensitive operations."""
    return admin_security(
        require_2fa=True,
        require_super_admin=require_super_admin,
        rate_limit="5/minute",
        audit_log=True,
        check_ip_whitelist=True,
    )


def get_admin_security_context() -> Optional[AdminSecurityConfig]:
    """Get the security context for the current admin request."""
    return getattr(g, "admin_security_config", None)


def get_admin_security_user():
    """Get the admin user that triggered the security check."""
    return getattr(g, "admin_security_user", None)
