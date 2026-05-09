# UDQ Sprint 3A — Guided U6 Field Validation and Auto-Diagnostic Packaging

## Purpose
Sprint 3A is a bounded follow-on to Sprint 3. It does not widen the architecture claim line. It prepares the next real-world U6 run so the operator can perform a short guided unplug/reconnect sequence and receive one bundled diagnostic package with minimal manual work.

## What this sprint changes
1. Upgrades the existing U6 field-test harness into a guided field-validation flow.
2. Adds preflight reporting before the nominal/disconnect/recovery/stabilization sequence.
3. Adds explicit phase records with expected-vs-observed runtime posture.
4. Adds automatic semantic-consistency checks and a machine-readable verdict.
5. Adds a top-level `START_HERE__U6_FIELD_VALIDATION.txt` plus an artifact manifest.
6. Preserves anti-truncation discipline with a new baseline snapshot, touched-file ledger, and truncation-guard report.

## Operator flow
1. Launch `tools\dev\run_u6_field_test_harness.bat`.
2. Confirm the U6 is connected.
3. Let the harness capture the baseline window.
4. Unplug the U6 when prompted.
5. Reconnect the U6 when prompted.
6. Wait for the stabilization window and automatic packaging.
7. Return the generated artifact directory for review.

## Output contract
The guided field-validation run now produces:
- preflight report (JSON + text)
- phase timeline in diagnostics JSON
- semantic consistency verdict (JSON + text)
- top-level start-here file
- markdown summary for first-pass review
- events CSV
- diagnostics JSON
- smoke summary
- artifact manifest (JSON + text)

## Bounded no-go areas
- no new hardware families
- no controller-collapse or large service split
- no broad historian/export redesign
- no UI redesign beyond documentation and evidence-surface references
- no support-pack leakage into universal core code
