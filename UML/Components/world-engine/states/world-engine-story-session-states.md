# Story session lifecycle

```mermaid
stateDiagram-v2
  [*] --> Created
  Created --> Active : start / first turn
  Active --> Active : successful turn
  Active --> Degraded : adapter degradation
  Degraded --> Active : recovery turn
  Active --> Ended : terminal scene / end condition
  Ended --> [*]
```

Source: [`world-engine-story-session-states.puml`](world-engine-story-session-states.puml)
