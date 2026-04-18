# fy Command Reference

This page lists the stable shared lifecycle commands and the suite-specific native commands.

- command_envelope_current: `fy.command-envelope.v4`
- supported_read_versions: `fy.command-envelope.v3, fy.command-envelope.v4`
- supported_write_versions: `fy.command-envelope.v4`

## Generic lifecycle commands

- `init`
- `inspect`
- `audit`
- `explain`
- `prepare-context-pack`
- `compare-runs`
- `clean`
- `reset`
- `triage`
- `prepare-fix`
- `self-audit`
- `release-readiness`
- `production-readiness`

## Suite-native commands

### contractify

- `consolidate`
- `import`
- `legacy-import`

### despaghettify

- `wave-plan`

### docify

- `inline-explain`

### dockerify

- `stack-audit`

### documentify

- `generate-track`

### metrify

- `pricing`
- `record`
- `ingest`
- `report`
- `ai-pack`
- `full`

### mvpify

- `inspect`
- `plan`
- `ai-pack`
- `full`

### observifyfy

- `inspect`
- `audit`
- `ai-pack`
- `full`

### postmanify

- `sync`

### securify

- `scan`
- `evaluate`
- `autofix`

### templatify

- `list-templates`
- `validate`
- `render`
- `check-drift`

### testify

- no additional native commands

### usabilify

- `inspect`
- `evaluate`
- `full`
