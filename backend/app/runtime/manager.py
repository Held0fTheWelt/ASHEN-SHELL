from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import WebSocket

from app.config import RUN_STORE_BACKEND, RUN_STORE_URL
from app.content.builtins import load_builtin_templates
from app.content.models import ExperienceKind, ExperienceTemplate, JoinPolicy, ParticipantMode, RoleTemplate
from app.runtime.engine import RuntimeEngine
from app.runtime.models import LobbySeatState, ParticipantState, PropState, PublicRunSummary, RunStatus, RuntimeInstance
from app.runtime.store import RunStore, build_run_store


class RuntimeManager:
    def __init__(
        self,
        store_root: Path,
        *,
        store_backend: str | None = None,
        store_url: str | None = None,
    ) -> None:
        self.templates: dict[str, ExperienceTemplate] = load_builtin_templates()
        self.instances: dict[str, RuntimeInstance] = {}
        self.engines: dict[str, RuntimeEngine] = {}
        self.connections: dict[str, dict[str, WebSocket]] = defaultdict(dict)
        self.locks: dict[str, asyncio.Lock] = {}
        self.store: RunStore = build_run_store(
            root=store_root,
            backend=store_backend or RUN_STORE_BACKEND,
            url=store_url if store_url is not None else RUN_STORE_URL,
        )
        self._load_persisted_instances()
        self._ensure_public_open_worlds()

    def _load_persisted_instances(self) -> None:
        for instance in self.store.load_all():
            template = self.templates.get(instance.template_id)
            if template is None:
                continue
            self._normalize_instance(instance, template)
            self.instances[instance.id] = instance
            self.engines[instance.id] = RuntimeEngine(template)
            self.locks.setdefault(instance.id, asyncio.Lock())

    def _ensure_public_open_worlds(self) -> None:
        for template in self.templates.values():
            if template.persistent and template.join_policy == JoinPolicy.PUBLIC:
                existing = next((run for run in self.instances.values() if run.template_id == template.id), None)
                if existing is None:
                    self._bootstrap_instance(template, owner_display_name=None, forced_run_id=f"public-{template.id}")

    def list_templates(self) -> list[ExperienceTemplate]:
        return list(self.templates.values())

    def list_runs(self) -> list[PublicRunSummary]:
        summaries: list[PublicRunSummary] = []
        for instance in sorted(self.instances.values(), key=lambda item: item.created_at):
            human_participants = [p for p in instance.participants.values() if p.mode == ParticipantMode.HUMAN]
            connected_humans = len([p for p in human_participants if p.connected])
            total_humans = len(human_participants)
            seats = list(instance.lobby_seats.values())
            summaries.append(
                PublicRunSummary(
                    id=instance.id,
                    template_id=instance.template_id,
                    template_title=instance.template_title,
                    kind=instance.kind,
                    join_policy=instance.join_policy,
                    persistent=instance.persistent,
                    status=instance.status,
                    connected_humans=connected_humans,
                    total_humans=total_humans,
                    open_human_seats=len([seat for seat in seats if seat.participant_id is None]),
                    ready_human_seats=len([seat for seat in seats if seat.ready]),
                    tension=instance.tension,
                    beat_id=instance.beat_id,
                    owner_player_name=instance.owner_player_name,
                )
            )
        return summaries

    def get_template(self, template_id: str) -> ExperienceTemplate:
        return self.templates[template_id]

    def create_run(
        self,
        template_id: str,
        display_name: str,
        account_id: str | None = None,
        character_id: str | None = None,
    ) -> RuntimeInstance:
        template = self.get_template(template_id)
        return self._bootstrap_instance(
            template,
            owner_display_name=display_name,
            owner_account_id=account_id,
            owner_character_id=character_id,
        )

    def _bootstrap_instance(
        self,
        template: ExperienceTemplate,
        owner_display_name: str | None,
        owner_account_id: str | None = None,
        owner_character_id: str | None = None,
        forced_run_id: str | None = None,
    ) -> RuntimeInstance:
        instance = RuntimeInstance(
            id=forced_run_id or uuid4().hex,
            template_id=template.id,
            template_title=template.title,
            kind=template.kind,
            join_policy=template.join_policy,
            owner_player_name=owner_display_name,
            owner_account_id=owner_account_id,
            owner_character_id=owner_character_id,
            beat_id=template.initial_beat_id,
            status=self._initial_status_for(template),
            persistent=template.persistent,
        )
        instance.metadata.setdefault("store_backend", self.store.backend_name)
        instance.metadata.setdefault("min_humans_to_start", template.min_humans_to_start)
        self._initialize_lobby_seats(instance, template)

        for role in template.roles:
            if role.mode == ParticipantMode.NPC:
                npc = ParticipantState(
                    display_name=role.display_name,
                    role_id=role.id,
                    mode=role.mode,
                    current_room_id=role.initial_room_id,
                    connected=True,
                )
                instance.participants[npc.id] = npc
        for prop in template.props:
            room_id = next(room.id for room in template.rooms if prop.id in room.prop_ids)
            instance.props[prop.id] = PropState(
                id=prop.id,
                name=prop.name,
                description=prop.description,
                room_id=room_id,
                state=prop.initial_state,
            )
        self.instances[instance.id] = instance
        self.engines[instance.id] = RuntimeEngine(template)
        self.locks.setdefault(instance.id, asyncio.Lock())
        self.store.save(instance)

        if owner_display_name:
            joinable_roles = [role for role in template.roles if role.mode == ParticipantMode.HUMAN and role.can_join]
            if not joinable_roles:
                raise ValueError(f"Template {template.id} has no joinable human roles")
            role = joinable_roles[0]
            participant = self._attach_human_participant(
                instance,
                role,
                display_name=owner_display_name,
                account_id=account_id_or_none(owner_account_id),
                character_id=owner_character_id,
                set_owner=True,
            )
            if template.kind == ExperienceKind.SOLO_STORY:
                instance.status = RunStatus.RUNNING
                instance.lobby_seats[participant.role_id].ready = True
            instance.updated_at = datetime.now(timezone.utc)
            self.store.save(instance)
        return instance

    def _initialize_lobby_seats(self, instance: RuntimeInstance, template: ExperienceTemplate) -> None:
        instance.lobby_seats = {
            role.id: LobbySeatState(role_id=role.id, role_display_name=role.display_name)
            for role in template.roles
            if role.mode == ParticipantMode.H