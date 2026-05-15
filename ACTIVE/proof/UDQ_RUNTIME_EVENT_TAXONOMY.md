# UniversalDAQ — Runtime Event Taxonomy

## Categories
- `runtime_event` — meaningful runtime-observed transitions.
- `alarm_event` — alarm lifecycle transitions/status rows.
- `operator_action` — governed human or command actions.
- `automation_claim` — claim/suppression continuity used primarily for engineering review.
- `diagnostic_snapshot` — counters/snapshots/journal-style evidence that does not claim a discrete incident.

## Rule
Diagnostics snapshots remain snapshots. They are not promoted into incidents merely because they are useful.
