# UDQ U6 Guided Field Validation Spec

## Goal
Create a low-interaction real-hardware validation flow that captures a truthful runtime story across baseline, disconnect, recovery, and stabilization, then packages the results for return review.

## Required phases
| Phase | Intent | Expected posture |
|---|---|---|
| `baseline` | confirm nominal live operation before disturbance | `live_ready_healthy` |
| `device_loss_window` | observe degradation/disconnect after operator unplug | `degraded` / `disconnected` / `recovering` / `faulted` |
| `recovery_window` | observe reconnect and bounded recovery behavior | `recovering` or `live_ready_healthy` |
| `post_recovery_stabilization` | confirm the slice settles back to a healthy live posture | `live_ready_healthy` |

## Required generated files
- `START_HERE__U6_FIELD_VALIDATION.txt`
- `u6_field_validation_summary.md`
- `*__preflight_report.json`
- `*__preflight_report.txt`
- `*__semantic_consistency_verdict.json`
- `*__semantic_consistency_verdict.txt`
- `*__events.csv`
- `*__diagnostics.json`
- `*__smoke.txt`
- `*__artifact_manifest.json`
- `*__artifact_manifest.txt`

## Preflight contents
- package identity
- Python/platform summary
- requested and entered hardware mode
- discovered device inventory
- selected serial number
- profile id
- output directory
- journal path
- stale artifact count in output root

## Semantic checks
The harness now auto-checks for:
- reviewer rollup vs canonical bundle state alignment
- final phase vs reviewer rollup consistency
- strict phase expectation failures
- operator marker distinctness
- disconnect and recovery evidence continuity
- phase-record completeness
- extra real-hardware checks when `--real-hardware` is used

## Acceptance posture
A simulated run should normally produce `PASS`. A real-hardware run may produce `PASS`, `PASS WITH ADVISORIES`, or `FAIL` depending on what the bundle records.
