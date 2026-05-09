# UDQ Run 3 Plan — `20260323_05_events_alarms_spine`

## Purpose
Add the first bounded operational-semantics layer on top of the runtime spine and bounded live-value slice.

## Predicates carried in
- Runtime spine remains bounded and measured.
- Optional support-pack boundary remains intact.
- Real U6 bounded live-value slice exists and has already been proven.
- Variable-state semantics are explicit enough to build on.

## Scope
- canonical event model
- canonical bounded alarm model
- transition-based raise/ack/clear semantics
- duplicate suppression for repeated active cycles
- review-bundle alarm/event summary surfaces
- append-only journal integration
- bounded real/sim U6 proof scenario

## Explicit non-goals
- rich dashboard/alarm console
- routing/notification subsystem
- rules engine
- sequence engine
- command arbitration expansion
- broad UI work

## Acceptance conditions
- events/alarms derive from canonical runtime truth
- repeated active cycles do not spam duplicate raises
- alarm acknowledgment is distinct from clearing
- event/alarm transitions are journaled through the canonical runtime path
- support-pack-specific alarm logic does not leak into core orchestration
- proof remains easy to reproduce
