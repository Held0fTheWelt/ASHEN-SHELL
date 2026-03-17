# `/runtime` Command - Execution Mode Switcher

Switch ClaudeClockwork execution modes on-demand from Claude Code CLI.

## Quick Start

```
/runtime              # Show interactive menu
/runtime get          # Show current mode
/runtime list         # List all modes
/runtime set adaptive # Switch mode
/runtime info         # Show details
```

## Modes

- **default** - Pure Ollama: Local, fast, no API costs
- **adaptive** - Smart routing: Ollama + Claude, optimal per task
- **claude-min** - Claude only: Highest quality

## Usage Examples

### Check current mode
```
/runtime get
```

### Switch to Adaptive mode
```
/runtime set adaptive
```

### Show all available modes
```
/runtime list
```

### Interactive menu
```
/runtime
```

## Use Cases

- **default**: Development, testing, privacy-sensitive work
- **adaptive**: Mixed workloads, automatic optimization
- **claude-min**: Production, quality-critical tasks

## Technical Details

Mode state: `/mnt/d/ClaudeClockwork/.claude/state/mode_state.json`

Changes take effect immediately for all future executions.
