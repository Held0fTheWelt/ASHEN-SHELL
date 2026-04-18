# Usabilify evaluation report

## frontend

- target_root: `frontend/templates`
- template_count: `15`
- average_score: `93.2`
- contracts: `docs/dev/play_shell_ux.md, docs/ADR/adr-0020-debug-panel-ui.md, docs/ADR/adr-0016-frontend-backend-restructure.md, docs/technical/runtime/player_input_interpretation_contract.md, docs/technical/architecture/session_runtime_contract.md, docs/technical/architecture/backend-runtime-classification.md`
- priority views:
  - `forgot_password.html` score `90`
    - info: Interactive surface lacks visible status/error signaling patterns.
  - `login.html` score `90`
    - info: Interactive surface lacks visible status/error signaling patterns.
  - `register.html` score `90`
    - info: Interactive surface lacks visible status/error signaling patterns.
  - `resend_verification.html` score `90`
    - info: Interactive surface lacks visible status/error signaling patterns.
  - `reset_password.html` score `90`
    - info: Interactive surface lacks visible status/error signaling patterns.

## administration_tool

- target_root: `administration-tool/templates`
- template_count: `56`
- average_score: `96.7`
- contracts: `docs/dev/play_shell_ux.md, docs/dev/world_engine_console_a11y.md, docs/dev/world_engine_console_wireframes.md, docs/ADR/adr-0020-debug-panel-ui.md, docs/technical/architecture/backend-runtime-classification.md`
- warnings:
  - Skip-link pattern already visible in base surface.
- priority views:
  - `base_manage.html` score `85`
    - warn: View has neither explicit heading tags nor a title block override.
    - info: View has no obvious interactive affordances; verify this is intentional.
  - `manage/game_content.html` score `90`
    - info: Interactive surface lacks visible status/error signaling patterns.
  - `manage/research_governance/_subnav.html` score `90`
    - warn: View has neither explicit heading tags nor a title block override.
  - `manage/dashboard.html` score `92`
    - info: Interactive elements exist but accessible naming signals are sparse.
  - `manage/diagnosis.html` score `92`
    - info: Interactive elements exist but accessible naming signals are sparse.

## administration_manage

- target_root: `administration-tool/templates/manage`
- template_count: `41`
- average_score: `96.6`
- contracts: `docs/dev/play_shell_ux.md, docs/dev/world_engine_console_a11y.md, docs/dev/world_engine_console_wireframes.md, docs/ADR/adr-0020-debug-panel-ui.md, docs/technical/architecture/backend-runtime-classification.md`
- warnings:
  - Skip-link pattern already visible in base surface.
- priority views:
  - `game_content.html` score `90`
    - info: Interactive surface lacks visible status/error signaling patterns.
  - `research_governance/_subnav.html` score `90`
    - warn: View has neither explicit heading tags nor a title block override.
  - `dashboard.html` score `92`
    - info: Interactive elements exist but accessible naming signals are sparse.
  - `diagnosis.html` score `92`
    - info: Interactive elements exist but accessible naming signals are sparse.
  - `game_operations.html` score `92`
    - info: Interactive elements exist but accessible naming signals are sparse.

## backend_info

- target_root: `backend/app/info/templates`
- template_count: `9`
- average_score: `94.4`
- contracts: `docs/dev/play_shell_ux.md, docs/dev/world_engine_console_a11y.md, docs/dev/world_engine_console_wireframes.md, docs/ADR/adr-0016-frontend-backend-restructure.md, docs/technical/runtime/player_input_interpretation_contract.md, docs/technical/architecture/session_runtime_contract.md, docs/technical/content/writers-room-and-publishing-flow.md, docs/technical/architecture/backend-runtime-classification.md`
- priority views:
  - `info_sections.html` score `82`
    - warn: View has neither explicit heading tags nor a title block override.
    - info: Interactive elements exist but accessible naming signals are sparse.
  - `ai.html` score `92`
    - info: Interactive elements exist but accessible naming signals are sparse.
  - `api_explorer.html` score `92`
    - info: Interactive elements exist but accessible naming signals are sparse.
  - `engine.html` score `92`
    - info: Interactive elements exist but accessible naming signals are sparse.
  - `ops.html` score `92`
    - info: Interactive elements exist but accessible naming signals are sparse.

## writers_room

- target_root: `writers-room/app/templates`
- template_count: `3`
- average_score: `93.3`
- contracts: `docs/technical/content/writers-room-and-publishing-flow.md`
- warnings:
  - Skip-link pattern already visible in base surface.
- priority views:
  - `index.html` score `90`
    - info: Interactive surface lacks visible status/error signaling patterns.
  - `login.html` score `90`
    - info: Interactive surface lacks visible status/error signaling patterns.
  - `base.html` score `100`
