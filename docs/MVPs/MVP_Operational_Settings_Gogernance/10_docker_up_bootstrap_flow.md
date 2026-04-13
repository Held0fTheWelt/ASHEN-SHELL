# 10 docker-up.py Bootstrap Flow

## Intent

`docker-up.py` must become the discoverable entry point for first configuration.

It must not silently assume the operator already knows:
- where bootstrap lives
- where trust-anchor setup lives
- where provider credentials are configured
- how to switch between mock, AI, or hybrid

## Required startup behavior

### Case A: system uninitialized
`docker-up.py` must:
1. detect uninitialized bootstrap state
2. tell the operator clearly that setup is required
3. launch or offer the bootstrap setup suite
4. provide a URL or embedded browser opening if web-first setup is available
5. optionally provide CLI-guided fallback
6. refuse to pretend normal startup is complete until bootstrap prerequisites are satisfied

### Case B: system initialized
`docker-up.py` may:
- start normally
- show current active profile summary
- optionally offer quick links to admin UI
- optionally offer protected bootstrap recovery entry

## Bootstrap web-first flow

Recommended flow:
1. lightweight bootstrap web service or app mode starts
2. `docker-up.py` prints the local setup URL and optionally opens browser
3. operator completes setup
4. backend records initialized state
5. `docker-up.py` continues to start the full stack or confirms readiness

## CLI fallback

If web setup cannot run, `docker-up.py` must support guided CLI fallback for:
- preset selection
- secret storage mode
- generation mode
- retrieval mode
- validation mode
- first provider metadata
- first secret input
- initial admin identity

## Presets

### Local Mock Safe
- mock only
- retrieval disabled or sparse only
- safe local runtime profile
- no external provider required

### Local Hybrid
- hybrid routed with mock fallback
- local provider preferred where configured
- optional cloud provider later
- balanced or cost-aware profile

### Cloud Narrative
- AI only or routed LLM/SLM
- cloud provider configured
- costs enabled
- quality-first or balanced profile

### Research / Evaluation
- hybrid or AI-focused
- preview/research routes emphasized
- evaluation-heavy profile

## Bootstrap completion artifact

At minimum record:
- bootstrap state
- trust-anchor mode
- selected preset
- selected modes
- initialized timestamp
- initialized by
- first provider setup state

## Failure handling

If bootstrap partially fails:
- state must be visible as incomplete
- `docker-up.py` must not hide the error
- the operator must know how to resume or recover

## Trust-anchor discoverability rule

The operator must never need to search source files to discover how the system was initially anchored.
`docker-up.py` and the admin UI must make this path visible.
