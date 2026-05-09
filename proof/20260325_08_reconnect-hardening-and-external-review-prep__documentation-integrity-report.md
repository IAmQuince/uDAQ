# 20260325_08 reconnect hardening and external-review prep — Documentation integrity report

## Summary
Pass A preserved package integrity while tightening review readiness for the current green real-U6 lane.

## Checks
- package-entry validation: PASS
- document completeness: PASS
- windows path budget: PASS
- run artifact naming validation for new `20260325_08` proof files: PASS
- truncation guard versus the `20260325_07` baseline snapshot: PASS

## Documentation posture after Pass A
- the package now contains the current authoritative real-hardware specimens under `proof/field_tests/`
- the startup-smoke advisory disposition is explicitly documented
- reconnect-attempt churn is explicitly explained as a non-blocking timing artifact of the intentional loss window in the current passing specimen
- release notes and next-actions now point reviewers toward the authoritative green proof story rather than older failing specimens
