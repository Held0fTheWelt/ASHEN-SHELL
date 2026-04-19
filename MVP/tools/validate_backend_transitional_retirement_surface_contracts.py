from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


CHECKS = {
    "backend/app/api/v1/session_routes.py": [
        "Live play runs in the World Engine",
        "backend_in_process_session_not_authoritative_live_runtime",
        "authoritative_runs_execute_in_world_engine_play_service",
        "world_engine_story_runtime_authoritative_snapshot",
        "execute_story_turn_in_engine",
        "get_story_state",
        "get_story_diagnostics",
    ],
    "backend/app/runtime/session_store.py": [
        "volatile in-memory registry",
        "authoritative for live play",
        "durable or",
        "data is lost on restart",
    ],
    "backend/app/services/session_service.py": [
        "live narrative runtime",
        "create_session: start a **local** session",
        "register in ``session_store``",
        "NotImplementedError",
    ],
    "backend/app/api/v1/world_engine_console_routes.py": [
        "Admin API: proxy read/write World Engine play service",
        "require_jwt_moderator_or_admin",
        "require_world_engine_capability",
        "/admin/world-engine/",
        "get_play_service_ready",
        "get_story_state",
        "get_story_diagnostics",
        "execute_story_turn",
    ],
}


NEGATIVE_CHECKS = {
    "backend/app/api/v1/world_engine_console_routes.py": [
        "session_store",
        '"/api/v1/sessions"',
    ]
}


def validate() -> dict[str, object]:
    files = []
    failures = []
    for rel, needles in CHECKS.items():
        path = REPO_ROOT / rel
        text = path.read_text(encoding="utf-8")
        present = []
        missing = []
        for needle in needles:
            (present if needle in text else missing).append(needle)
        negatives = []
        for needle in NEGATIVE_CHECKS.get(rel, []):
            if needle in text:
                negatives.append(needle)
        files.append(
            {
                "path": rel,
                "required_markers_present": present,
                "required_markers_missing": missing,
                "negative_markers_present": negatives,
                "status": "PASS" if not missing and not negatives else "FAIL",
            }
        )
        if missing or negatives:
            failures.append({"path": rel, "missing": missing, "unexpected": negatives})
    return {
        "status": "PASS" if not failures else "FAIL",
        "checked_files": len(files),
        "files": files,
        "failures": failures,
    }


if __name__ == "__main__":
    payload = validate()
    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if payload["status"] == "PASS" else 1)
