# UDQ U6 Runtime Fault Handling

## Bounded policy
- first runtime read failure transitions the adapter to `degraded`
- the backend is released so the next poll attempts a bounded reconnect
- persistent loss transitions to `disconnected`
- successful later polls transition back to `ready` with a recovery classification

## What this achieves
- clearer distinction between startup failure and runtime loss
- bounded reconnect attempts without pretending to implement a full device supervisor
- clearer reviewer-facing diagnostics through counters and state snapshots
