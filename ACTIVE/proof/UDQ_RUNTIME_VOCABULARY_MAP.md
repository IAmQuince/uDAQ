# UniversalDAQ — Runtime Vocabulary Map

## Layers
1. `ui_phase` — shell/operator-facing posture.
2. `lifecycle_summary_phase` — bounded review-bundle posture.
3. `adapter_lifecycle_state` — device/support-pack runtime condition.
4. `state_family` — normalized cross-layer semantic family.
5. `reviewer_label` — concise derived language for PM/reviewer rollups.

## Normalized families
- `configuration_pre_run`
- `initializing`
- `live_ready_healthy`
- `degraded`
- `disconnected`
- `recovering`
- `faulted`
- `shutting_down`
- `stopped`
- `unknown`

## Design rule
The package now treats apparently different tokens such as `ready`, `live`, and `ready_to_configure` as layer-specific terms that can be compared through one normalized family rather than flattened blindly.
