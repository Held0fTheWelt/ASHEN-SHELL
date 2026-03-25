from __future__ import annotations

from flask import jsonify, request

from app.api.v1 import api_v1_bp
from app.auth.feature_registry import FEATURE_MANAGE_GAME_CONTENT, FEATURE_MANAGE_GAME_OPERATIONS
from app.auth.permissions import get_current_user, require_feature, require_jwt_moderator_or_admin
from app.extensions import limiter
from app.services import log_activity
from app.services.game_content_service import (
    create_experience,
    get_experience,
    list_experiences,
    list_published_experiences,
    publish_experience,
    update_experience,
)
from app.services.game_service import GameServiceError, get_run_detail, get_run_transcript, list_runs as list_play_runs, terminate_run


def _experience_dict(item, *, include_published_payload: bool = False):
    return item.to_dict(include_payload=True, include_published_payload=include_published_payload)


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
    item, err = create_experience(
        key=data.get('key'),
        title=data.get('title'),
        experience_type=data.get('experience_type'),
        summary=data.get('summary'),
        tags=data.get('tags'),
        style_profile=data.get('style_profile'),
        draft_payload=data.get('draft_payload'),
        actor_id=user.id if user else None,
    )
    if err:
        return jsonify({'error': err}), 409 if 'exists' in err.lower() else 400
    log_activity(actor=user, category='game', action='experience_create', status='success', message=f'Created game experience {item.key}', route=request.path, method=request.method, target_type='game_experience', target_id=str(item.id))
    return jsonify(_experience_dict(item)), 201


@api_v1_bp.route('/game-admin/experiences/<int:experience_id>', methods=['GET'])
@limiter.limit('60 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_CONTENT)
def game_admin_get_experience(experience_id: int):
    item = get_experience(experience_id)
    if not item:
        return jsonify({'error': 'Experience not found'}), 404
    return jsonify(_experience_dict(item, include_published_payload=True)), 200


@api_v1_bp.route('/game-admin/experiences/<int:experience_id>', methods=['PUT'])
@limiter.limit('30 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_CONTENT)
def game_admin_update_experience(experience_id: int):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Invalid or missing JSON body'}), 400
    user = get_current_user()
    item, err = update_experience(
        experience_id,
        title=data.get('title') if 'title' in data else None,
        experience_type=data.get('experience_type') if 'experience_type' in data else None,
        summary=data.get('summary') if 'summary' in data else None,
        tags=data.get('tags') if 'tags' in data else None,
        style_profile=data.get('style_profile') if 'style_profile' in data else None,
        draft_payload=data.get('draft_payload') if 'draft_payload' in data else None,
        status=data.get('status') if 'status' in data else None,
        actor_id=user.id if user else None,
    )
    if err:
        return jsonify({'error': err}), 404 if 'not found' in err.lower() else 400
    log_activity(actor=user, category='game', action='experience_update', status='success', message=f'Updated game experience {item.key}', route=request.path, method=request.method, target_type='game_experience', target_id=str(item.id))
    return jsonify(_experience_dict(item, include_published_payload=True)), 200


@api_v1_bp.route('/game-admin/experiences/<int:experience_id>/publish', methods=['POST'])
@limiter.limit('20 per minute')
@require_jwt_moderator_or_admin
@require_feature(FEATURE_MANAGE_GAME_CONTENT)
def game_admin_publish_experience(experience_id: int):
    user = get_current_user()
    item, err = publish_experience(experience_id, actor_id=user.id if user else None)
    if err:
        return jsonify({'error': err}), 404 if 'not found' in err.lower() else 400
    log_activity(actor=user, category='game', action='experience_publish', status='success', message=f'Published game experience {item.key} version {item.published_version}', route=request.path, method=request.method, target_type='game_experience', target_id=str(item.id))
    return jsonify(_experience_dict(item, include_published_payload=True)), 200


@api_v1_bp.route('/game-content/templates', methods=['GET'])
@limiter.limit('120 per minute')
def game_content_published_feed():
    return jsonify({'items': list_published_experiences()}), 200


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
        return jsonify(get_run_detail(run_id)), 200
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
