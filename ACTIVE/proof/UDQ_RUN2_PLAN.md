# UDQ Run 2 Plan

## Run
`20260323_04_bounded_live_value`

## Purpose
Deepen the already-proven bounded live monitoring slice into a bounded live-value slice with derived variables, explicit variable-state semantics, durable session truth, and a real U6 diagnostic/smoke deliverable.

## Predicate gates
- Run 1 runtime spine must remain intact.
- Core must still boot with zero support packs installed.
- Support packs must remain optional and lazy.
- Variable evaluation must remain changed-signal scoped.
- Package story must remain narrow and value-led.

## Code scope
- journal bounded variable updates and state transitions
- preserve bounded acquisition/presentation/persistence runtime lanes
- expose current variable snapshots and recent variable transitions in lifecycle review output
- extend the U6 smoke path into a bounded live-value smoke path with nonzero variables
- add a no-edit real U6 diagnostic harness and live-value smoke harness

## Out of scope
- alarms/events subsystem
- command admission
- rules/sequences
- streaming
- broad UI redesign
- broad documentation sweep

## Deliverables
- bounded variable update journaling
- lifecycle review bundle variable rows
- `tools\dev\run_u6_diag.bat`
- `tools\dev\run_u6_live_smoke.bat`
- `tools/dev/run_u6_diag.py`
- `tools/dev/run_u6_live_value_smoke.py`
- concise real-U6 proof instructions
