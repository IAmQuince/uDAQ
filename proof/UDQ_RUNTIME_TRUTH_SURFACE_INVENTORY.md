# UniversalDAQ — Runtime Truth Surface Inventory

## Canonical/derived surfaces now carried in the lifecycle review bundle

| Surface | Owner module | Audience | Authority | Purpose |
|---|---|---|---|---|
| `lifecycle_summary` | `src/universaldaq/app/lifecycle_orchestrator.py` | reviewer + engineering | derived review surface | bounded lifecycle posture |
| `active_adapter_status` | `src/universaldaq/app/device_lifecycle_handler.py` | engineering with reviewer support | device/support-pack surface | device condition and recovery counters |
| `runtime_status` | `src/universaldaq/runtime/services.py` | engineering | canonical runtime snapshot | queue, journal, and presentation status |
| `recent_runtime_event_rows` | `src/universaldaq/runtime/services.py` | reviewer + engineering | runtime event surface | meaningful runtime transitions |
| `recent_event_rows` | `src/universaldaq/events/services.py` | reviewer + engineering | alarm event surface | alarm lifecycle transitions |
| `recent_command_rows` | `src/universaldaq/commands/services.py` | reviewer + engineering | operator action surface | governed operator/command actions |
| `recent_action_claim_rows` | `src/universaldaq/automation/claims.py` | engineering | automation claim surface | claim/suppression continuity |
| `runtime_performance` | `src/universaldaq/common/metrics.py` | engineering | runtime metrics snapshot | timings, counters, gauges |
| `reviewer_runtime_rollup` | `src/universaldaq/app/automation_review_handler.py` | reviewer | derived rollup | concise reviewer-facing statement from canonical truth |

## Inventory conclusion
The bundle now makes the distinction between runtime truth producers and reviewer-facing renderers explicit instead of forcing the reviewer to infer it from unrelated sections.
