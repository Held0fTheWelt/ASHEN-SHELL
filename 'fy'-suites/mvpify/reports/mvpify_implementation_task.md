# MVPify implementation task

You are implementing a prepared MVP import into the live repository.

- Imported source: `/mnt/data/world_of_shadows_mvp_v24_backend_transitional_retirement_ultra_narrow_final_blockers.zip`
- Current highest-value suite after import: `contractify`
- Mirrored docs root: `docs/MVPs/imports/world-of-shadows-mvp-v24-backend-transitional-retirement-ultra-narrow-final-blockers-8529b8af`

## Operating discipline

- Import the prepared MVP content into the repository without losing the existing suite governance.
- Mirror imported MVP docs into docs/MVPs/imports/<id> so they stay available after temporary implementation folders are removed.
- Use contractify for contract/governance attachment when relevant.
- Use despaghettify to pick the smallest coherent implementation insertion path.
- Use testify and runtime-specialist suites before declaring the imported work operational.
- Refresh documentation and internal suite tracking after implementation.

## Ordered execution plan

### 1. import / mvpify

Normalize the prepared MVP bundle into a governed internal import inventory.

Why now: Prepared MVP information exists but must become explicit and restartable before implementation work starts.

Inputs:
- /tmp/mvpify-import-8jmfn911/base

Expected outputs:
- mvpify/reports/mvpify_import_inventory.json
- mvpify/reports/mvpify_import_inventory.md

### 2. governance / contractify

Attach the imported MVP contracts, ADRs, and runtime/MVP spine to governed records.

Why now: The imported MVP already contains governance surfaces that must become first-class before implementation drift begins.

Inputs:
- mvpify import inventory
- docs/ADR
- runtime/MVP docs

Expected outputs:
- contract audit update
- attachment report
- runtime/MVP spine state

### 3. structure / despaghettify

Assess structural drift and pick the smallest safe implementation surface for the next coding pass.

Why now: Prepared MVP plans only help if the code insertion path is scoped and coherent.

Inputs:
- mvpify import inventory
- current repo tree
- existing despaghettify workstreams

Expected outputs:
- workstream state update
- next structural insertion target

### 4. verification / testify

Align tests, CI gates, and suite execution metadata with the imported MVP change set.

Why now: Implementation cannot be trusted unless test and CI surfaces are ready to carry the change.

Inputs:
- implementation task draft
- tests/run_tests.py
- GitHub workflows
- pyproject.toml

Expected outputs:
- test audit update
- recommended gate set

### 5. runtime_validation / dockerify

Validate startup, compose topology, database readiness, and smoke paths for the MVP insertion.

Why now: The imported MVP targets runtime behavior, so stable boot evidence matters immediately after implementation.

Inputs:
- implementation task draft
- docker-up.py
- docker-compose.yml

Expected outputs:
- docker audit update
- startup/stability findings

### 6. documentation / documentify

Refresh easy, technical, role-based, and AI-facing docs after the MVP import is applied.

Why now: Imported MVP plans lose value if the resulting repository state is not explained and searchable.

Inputs:
- implementation task draft
- current docs
- technical docs
- contract/docs findings

Expected outputs:
- documentify generation update
- AI context pack refresh

