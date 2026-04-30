"""
Multi-layer security decorator for admin endpoints.

Implements comprehensive security checks:
1. JWT and admin role verification
2. Role level verification (SuperAdmin for sensitive operations)
3. IP whitelist enforcement (if configured)
4. Per-admin rate limiting
5. 2FA verification for sensitive operations
6. Comprehensive audit logging
7. Override audit trail with configurable granularity
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional

from flask import current_app, g, jsonify, request
from flask_jwt_extended import jwt_required

from app.auth import admin_security_helpers
from app.auth.admin_security_helpers import _get_client_ip
from app.auth.admin_security_policy import AdminSecurityConfig, evaluate_admin_security_gate
from app.auth.permissions import get_current_user

logger = logging.getLogger(__name__)

_rate_limit_cache = admin_security_helpers._rate_limit_cache


class OverrideEventType(Enum):
    """Event types for override audit trail."""
    CREATED = "created"                   # Override created
    APPLY_ATTEMPT = "apply_attempt"       # Attempted to apply
    APPLIED = "applied"                   # Successfully applied
    APPLY_FAILED = "apply_failed"         # Application failed
    REVOKED = "revoked"                   # Revocation successful
    REVOKE_FAILED = "revoke_failed"       # Revocation failed
    ACCESSED = "accessed"                 # Super-admin accessed debug_payload


@dataclass
class OverrideAuditEvent:
    """Audit event for override operations."""
    event_type: OverrideEventType
    override_id: str
    admin_user: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: Optional[str] = None
    turn_number: Optional[int] = None
    reason: Optional[str] = None
    error_message: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "override_id": self.override_id,
            "admin_user": self.admin_user,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "reason": self.reason,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "OverrideAuditEvent":
        return OverrideAuditEvent(
            event_type=OverrideEventType(data.get("event_type")),
            override_id=data.get("override_id", ""),
            admin_user=data.get("admin_user", ""),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            session_id=data.get("session_id"),
            turn_number=data.get("turn_number"),
            reason=data.get("reason"),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class OverrideAuditConfig:
    """Configure which override events to log per override type."""
    override_type: str  # "object_admission", "state_delta_boundary", etc.
    log_created: bool = True
    log_apply_attempt: bool = True
    log_applied: bool = True
    log_apply_failed: bool = True
    log_revoked: bool = True
    log_revoke_failed: bool = True
    log_accessed: bool = True

    def should_log(self, event_type: OverrideEventType) -> bool:
        """Check if event type should be logged based on config."""
        mapping = {
            OverrideEventType.CREATED: self.log_created,
            OverrideEventType.APPLY_ATTEMPT: self.log_apply_attempt,
            OverrideEventType.APPLIED: self.log_applied,
            OverrideEventType.APPLY_FAILED: self.log_apply_failed,
            OverrideEventType.REVOKED: self.log_revoked,
            OverrideEventType.REVOKE_FAILED: self.log_revoke_failed,
            OverrideEventType.ACCESSED: self.log_accessed,
        }
        return mapping.get(event_type, True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "override_type": self.override_type,
            "log_created": self.log_created,
            "log_apply_attempt": self.log_apply_attempt,
            "log_applied": self.log_applied,
            "log_apply_failed": self.log_apply_failed,
            "log_revoked": self.log_revoked,
            "log_revoke_failed": self.log_revoke_failed,
            "log_accessed": self.log_accessed,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "OverrideAuditConfig":
        return OverrideAuditConfig(
            override_type=data.get("override_type", ""),
            log_created=data.get("log_created", True),
            log_apply_attempt=data.get("log_apply_attempt", True),
            log_applied=data.get("log_applied", True),
            log_apply_failed=data.get("log_apply_failed", True),
            log_revoked=data.get("log_revoked", True),
            log_revoke_failed=data.get("log_revoke_failed", True),
            log_accessed=data.get("log_accessed", True),
        )

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
    "OverrideEventType",
    "OverrideAuditEvent",
    "OverrideAuditConfig",
    "OverrideAuditConfigManager",
    "_check_rate_limit",
    "_get_client_ip",
    "_is_ip_whitelisted",
    "_log_admin_action",
    "_log_override_event",
    "_log_security_violation",
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


def _log_override_event(
    event: OverrideAuditEvent,
    config: OverrideAuditConfig,
    user: Optional[Any] = None,
) -> bool:
    """Log override audit event if granularity config allows.

    Returns True if event was logged, False if filtered by granularity config.
    """
    if not config.should_log(event.event_type):
        logger.debug(
            f"Override event {event.event_type.value} filtered by granularity config"
        )
        return False

    status = "success" if event.event_type in (
        OverrideEventType.APPLIED,
        OverrideEventType.REVOKED,
        OverrideEventType.ACCESSED,
    ) else "pending"

    if event.event_type in (OverrideEventType.APPLY_FAILED, OverrideEventType.REVOKE_FAILED):
        status = "error"

    details = {
        "override_id": event.override_id,
        "event_type": event.event_type.value,
        "session_id": event.session_id,
        "turn_number": event.turn_number,
        "error_message": event.error_message,
        **event.metadata,
    }

    _log_admin_action(
        user=user or event.admin_user,
        action=f"override_{event.event_type.value}",
        resource=f"override:{event.override_id}",
        status=status,
        details=details,
    )

    logger.info(
        f"Override event logged: {event.event_type.value} for override {event.override_id}",
        extra={
            "event_type": "override_audit",
            "override_event_type": event.event_type.value,
            "override_id": event.override_id,
            "admin_user": event.admin_user,
            "session_id": event.session_id,
            "turn_number": event.turn_number,
            "timestamp": event.timestamp,
        },
    )

    return True


class OverrideAuditConfigManager:
    """Manage audit configuration per override type."""

    def __init__(self, session_storage: Optional[Any] = None):
        self.storage = session_storage
        # In-memory defaults for all override types
        self._defaults = {
            "object_admission": OverrideAuditConfig("object_admission"),
            "state_delta_boundary": OverrideAuditConfig("state_delta_boundary"),
        }

    def get_config(self, override_type: str) -> OverrideAuditConfig:
        """Get audit config for override type."""
        if not self.storage:
            return self._defaults.get(
                override_type, OverrideAuditConfig(override_type)
            )

        storage_key = f"override_audit_config:{override_type}"
        stored = self.storage.get(storage_key)

        if stored:
            if isinstance(stored, dict):
                return OverrideAuditConfig.from_dict(stored)
            return stored

        config = self._defaults.get(
            override_type, OverrideAuditConfig(override_type)
        )
        self.storage.set(storage_key, config)
        return config

    def set_config(self, config: OverrideAuditConfig) -> None:
        """Set audit config for override type."""
        if self.storage:
            storage_key = f"override_audit_config:{config.override_type}"
            self.storage.set(storage_key, config)
        else:
            self._defaults[config.override_type] = config

    def get_all_configs(self) -> dict[str, OverrideAuditConfig]:
        """Get all audit configs."""
        return dict(self._defaults)


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
