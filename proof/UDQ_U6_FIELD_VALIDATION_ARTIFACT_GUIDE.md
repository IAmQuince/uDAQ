# UDQ U6 Field Validation Artifact Guide

## Open these first
1. `START_HERE__U6_FIELD_VALIDATION.txt`
2. `u6_field_validation_summary.md`
3. `*__semantic_consistency_verdict.txt`
4. `*__summary.txt`
5. `*__preflight_report.txt`
6. `*__events.csv`
7. `*__diagnostics.json`

## What each file is for
- `START_HERE__U6_FIELD_VALIDATION.txt` — single-entry navigation for the returned bundle
- `u6_field_validation_summary.md` — compact reviewer-friendly summary
- `*__summary.txt` — fuller plain-text summary including phase timeline and check results
- `*__preflight_report.*` — environment/setup capture before the disturbance begins
- `*__semantic_consistency_verdict.*` — machine-generated PASS / PASS WITH ADVISORIES / FAIL verdict
- `*__events.csv` — flattened operator/harness/runtime/phase timeline export
- `*__diagnostics.json` — machine-readable master payload used for detailed review
- `*__artifact_manifest.*` — integrity-oriented list of all generated files
- `*__smoke.txt` — compact smoke/status summary for quick triage

## What to send back after a real run
At minimum, return:
- the entire generated artifact directory, or
- `START_HERE__U6_FIELD_VALIDATION.txt`
- `u6_field_validation_summary.md`
- `*__semantic_consistency_verdict.json`
- `*__diagnostics.json`
- `*__events.csv`
