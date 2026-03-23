import logging
import time
from datetime import datetime, timedelta, timezone

from flask import current_app, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt, jwt_required
from sqlalchemy import update

from app.api.v1 import api_v1_bp
from app.extensions import limiter, db
from app.models import User
from app.services import create_user, log_activity, verify_user
from app.services.token_service import generate_tokens, refresh_access_token, revoke_user_tokens
from app.services.user_service import (
    create_email_verification_token,
    get_user_by_username,
    validate_password_complexity,
    create_password_reset_token,
    reset_password_with_token,
    get_user_by_email,
    validate_email_format,
)
from app.services.mail_service import send_verification_email, send_password_reset_email
from app.utils.error_handler import log_full_error, ERROR_MESSAGES

logger = logging.getLogger(__name__)

# Constant-time delay (milliseconds) to prevent timing-based email enumeration attacks
CONSTANT_TIME_DELAY_SECONDS = 0.2


@api_v1_bp.route("/auth/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    """Register a new user; return 201 with id and username or error."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    username = (data.get("username") or "").strip()
    password = data.get("password")
    email_raw = data.get("email")
    # Normalize email to lowercase and strip whitespace before any operations
    email = (email_raw or "").strip().lower() if email_raw is not None else ""
    require_email = current_app.config.get("REGISTRATION_REQUIRE_EMAIL", False)
    if require_email and not email:
        return jsonify({"error": "Email is required"}), 400
    # Validate password complexity
    is_valid, error_msg = validate_password_complexity(password)
    if not is_valid:
        return jsonify({"error": error_msg, "code": "PASSWORD_WEAK"}), 400
    user, err = create_user(username, password, email or None)
    if err:
        status = 409 if err in ("Username already taken", "Email already registered") else 400
        return jsonify({"error": err}), status
    log_activity(
        actor=user,
        category="auth",
        action="register",
        status="success",
        message="API registration successful",
        route=request.path,
        method=request.method,
        tags=["api"],
    )
    if user.email:
        ttl = current_app.config.get("EMAIL_VERIFICATION_TTL_HOURS", 24)
        raw_token = create_email_verification_token(user, ttl_hours=ttl)
        send_verification_email(user, raw_token)
        log_activity(
            actor=user,
            category="auth",
            action="verification_email_sent",
            status="success",
            message="Verification email sent",
            route=request.path,
            method=request.method,
            tags=["api", "email"],
        )
    return jsonify({"id": user.id, "username": user.username}), 201


@api_v1_bp.route("/auth/login", methods=["POST"])
@limiter.limit("20 per minute")
def login():
    """Authenticate and return JWT access_token and user info."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    username = (data.get("username") or "").strip()
    password = data.get("password")
    if not username or password is None:
        return jsonify({"error": "Username and password are required"}), 400

    # Get user by username
    user = get_user_by_username(username)

    # Check if account is locked
    if user and user.locked_until:
        locked_until = user.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        if locked_until > datetime.now(timezone.utc):
            log_activity(
                actor=user,
                category="auth",
                action="login_blocked_locked",
                status="warning",
                message="API login attempted for locked account",
                route=request.path,
                method=request.method,
                tags=["api"],
            )
            return jsonify({"error": "Account temporarily locked. Try again in 15 minutes."}), 429

    # Verify credentials
    authenticated_user = verify_user(username, password)
    if authenticated_user:
        # Success: reset counter and lock timestamp using atomic update
        # This prevents race conditions in multi-threaded/multi-process environments
        db.session.execute(
            update(User)
            .where(User.id == authenticated_user.id)
            .values(failed_login_attempts=0, locked_until=None)
        )
        db.session.commit()

        # Refresh user object from database to get updated values
        authenticated_user = db.session.get(User, authenticated_user.id)

        if getattr(authenticated_user, "is_banned", False):
            log_activity(
                actor=authenticated_user,
                category="auth",
                action="login_blocked_banned",
                status="warning",
                message="API login attempted by banned user",
                route=request.path,
                method=request.method,
                tags=["api"],
            )
            return jsonify({"error": "Account is restricted."}), 403
        # Check email verification if REQUIRE_EMAIL_VERIFICATION_FOR_LOGIN is enabled
        # This enforces verification in production but allows it in dev/testing for easier testing
        if (
            current_app.config.get("REQUIRE_EMAIL_VERIFICATION_FOR_LOGIN", True)
            and authenticated_user.email
            and authenticated_user.email_verified_at is None
        ):
            log_activity(
                actor=authenticated_user,
                category="auth",
                action="login_blocked_unverified",
                status="warning",
                message="API login attempted before email verification",
                route=request.path,
                method=request.method,
                tags=["api"],
            )
            return jsonify({
                "error": "Please verify your email before logging in",
                "code": "EMAIL_NOT_VERIFIED"
            }), 403
        log_activity(
            actor=authenticated_user,
            category="auth",
            action="login",
            status="success",
            message="API login successful",
            route=request.path,
            method=request.method,
            tags=["api"],
        )
        tokens = generate_tokens(authenticated_user.id)
        return jsonify({
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": tokens["expires_at"],
            "expires_in": tokens["expires_in"],
            "refresh_expires_at": tokens["refresh_expires_at"],
            "user": authenticated_user.to_dict(include_email=True),
        }), 200

    # Failure: increment counter atomically using database UPDATE with WHERE
    # This ensures that even with concurrent requests, the counter is incremented exactly once
    # and account lockout is triggered atomically without race conditions
    if user:
        # Use atomic UPDATE to increment counter
        db.session.execute(
            update(User)
            .where(User.id == user.id)
            .values(failed_login_attempts=User.failed_login_attempts