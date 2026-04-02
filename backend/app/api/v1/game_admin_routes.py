from __future__ import annotations

from flask import jsonify, request

from app.api.v1 import api_v1_bp
from app.auth.feature_registry import FEATURE_MANAGE_GAME_CONTENT, FEATURE_MANAGE_GAME_OPERATIONS
from app.auth.permissions import get_current_user, require_feature, require_jwt_moderator_or_admin
from app.extensions import limiter
from app.services import log_activity
from app.services.game_content_service import (
    GameContentNotFoundError,
    create_experience,
    get_experience,
    list_experiences,
    list_published_experience_payloads,
    publish_experience,
    update_experience,
)
from app.services.game_service import GameServiceError, get_run_details, get_run_transcript, list_runs as list_play_runs, terminate_run


@api_v1_bp.route('/game-admin/experiences', methods=['GET'])
@limiter.limit('60 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_CONTENT)
def game_admin_list_experiences():
    q = (request.args.get('q') or '').strip() or None
    status = (request.args.get('status') or '').strip() or None
    include_payload = (request.args.get('include_payload') or '').strip().lower() in {'1', 'true', 'yes'}
    return jsonify({'items': list_experiences(q=q, status=status, include_payload=include_payload)}), 200


@api_v1_bp.route('/game-admin/experiences', methods=['POST'])
@limiter.limit('30 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_CONTENT)
def game_admin_create_experience():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Invalid or missing JSON body'}), 400
    user = get_current_user()
    try:
        # Build payload from request - draft_payload contains the full template structure
        payload = data.get('draft_payload', {})
        if not payload:
            return jsonify({'error': 'draft_payload is required'}), 400

        item = create_experience(
            payload=payload,
            actor_user_id=user.id if user else None,
        )
    except Exception as exc:
        error_msg = str(exc)
        return jsonify({'error': error_msg}), 409 if 'exists' in error_msg.lower() else 400

    log_activity(actor=user, category='game', action='experience_create', status='success', message=f'Created game experience {item["template_id"]}', route=request.path, method=request.method, target_type='game_experience', target_id=str(item['id']))
    return jsonify(item), 201


@api_v1_bp.route('/game-admin/experiences/<int:experience_id>', methods=['GET'])
@limiter.limit('60 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_CONTENT)
def game_admin_get_experience(experience_id: int):
    try:
        item = get_experience(experience_id, include_payload=True)
    except GameContentNotFoundError:
        return jsonify({'error': 'Experience not found'}), 404
    return jsonify(item), 200


@api_v1_bp.route('/game-admin/experiences/<int:experience_id>', methods=['PUT'])
@limiter.limit('30 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_CONTENT)
def game_admin_update_experience(experience_id: int):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Invalid or missing JSON body'}), 400
    user = get_current_user()
    try:
        # Build payload from draft_payload if provided
        payload = data.get('draft_payload', {})
        if not payload:
            return jsonify({'error': 'draft_payload is required'}), 400

        item = update_experience(
            experience_id,
            payload=payload,
            actor_user_id=user.id if user else None,
        )
    except Exception as exc:
        error_msg = str(exc)
        return jsonify({'error': error_msg}), 404 if 'not found' in error_msg.lower() else 400

    log_activity(actor=user, category='game', action='experience_update', status='success', message=f'Updated game experience {item["template_id"]}', route=request.path, method=request.method, target_type='game_experience', target_id=str(item['id']))
    return jsonify(item), 200


@api_v1_bp.route('/game-admin/experiences/<int:experience_id>/publish', methods=['POST'])
@limiter.limit('20 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_CONTENT)
def game_admin_publish_experience(experience_id: int):
    user = get_current_user()
    try:
        item = publish_experience(experience_id, actor_user_id=user.id if user else None)
    except Exception as exc:
        error_msg = str(exc)
        return jsonify({'error': error_msg}), 404 if 'not found' in error_msg.lower() else 400

    log_activity(actor=user, category='game', action='experience_publish', status='success', message=f'Published game experience {item["template_id"]}', route=request.path, method=request.method, target_type='game_experience', target_id=str(item['id']))
    return jsonify(item), 200


@api_v1_bp.route('/game-content/templates', methods=['GET'])
@limiter.limit('120 per minute')
def game_content_published_feed():
    return jsonify({'items': list_published_experience_payloads()}), 200


@api_v1_bp.route('/game-admin/runtime/runs', methods=['GET'])
@limiter.limit('60 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_OPERATIONS)
def game_admin_runtime_runs():
    try:
        return jsonify({'items': list_play_runs()}), 200
    except GameServiceError as exc:
        return jsonify({'error': str(exc)}), exc.status_code


@api_v1_bp.route('/game-admin/runtime/runs/<run_id>', methods=['GET'])
@limiter.limit('60 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_OPERATIONS)
def game_admin_runtime_run_detail(run_id: str):
    try:
        return jsonify(get_run_details(run_id)), 200
    except GameServiceError as exc:
        return jsonify({'error': str(exc)}), exc.status_code


@api_v1_bp.route('/game-admin/runtime/runs/<run_id>/transcript', methods=['GET'])
@limiter.limit('60 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_OPERATIONS)
def game_admin_runtime_run_transcript(run_id: str):
    try:
        return jsonify(get_run_transcript(run_id)), 200
    except GameServiceError as exc:
        return jsonify({'error': str(exc)}), exc.status_code


@api_v1_bp.route('/game-admin/runtime/runs/<run_id>/terminate', methods=['POST'])
@limiter.limit('20 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_OPERATIONS)
def game_admin_runtime_run_terminate(run_id: str):
    data = request.get_json(silent=True) or {}
    user = get_current_user()
    reason = (data.get('reason') or '').strip() or None
    try:
        payload = terminate_run(run_id, actor_display_name=user.username if user else 'moderator', reason=reason)
    except GameServiceError as exc:
        return jsonify({'error': str(exc)}), exc.status_code
    log_activity(actor=user, category='game', action='runtime_terminate', status='success', message=f'Terminated runtime run {run_id}', route=request.path, method=request.method, target_type='runtime_run', target_id=run_id)
    return jsonify(payload), 200
