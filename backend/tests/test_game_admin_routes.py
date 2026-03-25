from __future__ import annotations

from app.extensions import db
from app.models import GameExperienceTemplate


def _payload(template_id: str, kind: str = 'solo_story') -> dict:
    return {
        'id': template_id,
        'title': 'Apartment Incident',
        'kind': kind,
        'join_policy': 'owner_only' if kind == 'solo_story' else ('public' if kind == 'open_world' else 'invited_party'),
        'summary': 'Structured content payload for the runtime.',
        'max_humans': 1 if kind == 'solo_story' else 4,
        'initial_beat_id': 'intro',
        'roles': [
            {
                'id': 'visitor',
                'display_name': 'Visitor',
                'description': 'Human viewpoint role',
                'mode': 'human',
                'initial_room_id': 'hallway',
                'can_join': True,
            }
        ],
        'rooms': [
            {
                'id': 'hallway',
                'name': 'Hallway',
                'description': 'A narrow hallway.',
                'exits': [],
                'prop_ids': [],
                'action_ids': [],
            }
        ],
        'props': [],
        'actions': [],
        'beats': [
            {
                'id': 'intro',
                'name': 'Intro',
                'description': 'Opening beat',
                'summary': 'Opening beat',
            }
        ],
    }


def test_game_admin_create_and_publish_experience(client, moderator_headers, app):
    create_response = client.post(
        '/api/v1/game-admin/experiences',
        json={
            'key': 'god_of_carnage_group_authored',
            'title': 'God of Carnage — Authored Group',
            'experience_type': 'group_story',
            'summary': 'Author-managed group story.',
            'tags': ['group', 'authored'],
            'style_profile': 'retro_drama',
            'draft_payload': _payload('god_of_carnage_group_authored', kind='group_story'),
        },
        headers=moderator_headers,
    )
    assert create_response.status_code == 201
    item = create_response.get_json()
    assert item['key'] == 'god_of_carnage_group_authored'
    assert item['status'] == 'draft'

    publish_response = client.post(
        f"/api/v1/game-admin/experiences/{item['id']}/publish",
        headers=moderator_headers,
    )
    assert publish_response.status_code == 200
    published = publish_response.get_json()
    assert published['status'] == 'published'
    assert published['published_version'] == published['current_version']

    public_feed = client.get('/api/v1/game-content/templates')
    assert public_feed.status_code == 200
    feed_items = public_feed.get_json()['items']
    assert any(row['template_id'] == 'god_of_carnage_group_authored' for row in feed_items)


def test_game_admin_update_experience_increments_version(client, moderator_headers, app):
    with app.app_context():
        item = GameExperienceTemplate(
            key='bt_open_world_authored',
            title='Open World District',
            experience_type='open_world',
            summary='Initial summary',
            tags=['open-world'],
            style_profile='retro_pulp',
            status='draft',
            current_version=1,
            draft_payload=_payload('bt_open_world_authored', kind='open_world'),
        )
        db.session.add(item)
        db.session.commit()
        template_id = item.id

    response = client.put(
        f'/api/v1/game-admin/experiences/{template_id}',
        json={
            'summary': 'Updated summary',
            'draft_payload': {
                **_payload('bt_open_world_authored', kind='open_world'),
                'summary': 'Updated payload summary',
            },
        },
        headers=moderator_headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body['summary'] == 'Updated summary'
    assert body['current_version'] == 2
    assert body['draft_payload']['summary'] == 'Updated payload summary'


def test_game_admin_runtime_proxy_routes(client, moderator_headers, monkeypatch):
    monkeypatch.setattr('app.api.v1.game_admin_routes.list_play_runs', lambda: [{'id': 'run-1', 'template_id': 'god_of_carnage_solo'}])
    monkeypatch.setattr('app.api.v1.game_admin_routes.get_run_detail', lambda run_id: {'id': run_id, 'status': 'running', 'participants': []})
    monkeypatch.setattr('app.api.v1.game_admin_routes.get_run_transcript', lambda run_id: {'run_id': run_id, 'entries': [{'kind': 'speech_committed', 'text': 'hello'}]})
    monkeypatch.setattr('app.api.v1.game_admin_routes.terminate_run', lambda run_id, actor_display_name=None, reason=None: {'run_id': run_id, 'status': 'completed', 'reason': reason})

    runs = client.get('/api/v1/game-admin/runtime/runs', headers=moderator_headers)
    assert runs.status_code == 200
    assert runs.get_json()['items'][0]['id'] == 'run-1'

    detail = client.get('/api/v1/game-admin/runtime/runs/run-1', headers=moderator_headers)
    assert detail.status_code == 200
    assert detail.get_json()['status'] == 'running'

    transcript = client.get('/api/v1/game-admin/runtime/runs/run-1/transcript', headers=moderator_headers)
    assert transcript.status_code == 200
    assert transcript.get_json()['entries'][0]['kind'] == 'speech_committed'

    terminate = client.post('/api/v1/game-admin/runtime/runs/run-1/terminate', json={'reason': 'Moderation stop'}, headers=moderator_headers)
    assert terminate.status_code == 200
    assert terminate.get_json()['status'] == 'completed'
