# UDQ Sprint 03B — Reference Failure Specimen

This document freezes the first guided real-U6 return bundle as the reference failure specimen for Sprint 03B.

## Frozen artifact headlines
- bundle timestamp: `20260325_172005`
- semantic verdict: `FAIL`
- requested mode: `real`
- entered mode: `real`
- detected U6 serial: `360022207`

## Frozen failure facts
- `disconnect_count: 1`
- `recovery_count: 0`
- `session_recovered_after_disconnect: False`
- `post_disconnect_successful_poll_observed: False`
- `recovery_stage: backend_reopen_failed`
- disconnect phase rendered as `pre-run / configure` / `configuration_pre_run`
- semantic check `disconnect_has_runtime_evidence` failed
- stabilization remained `disconnected`

## Start-here excerpt
```text
START HERE — UDQ U6 Guided Field Validation
===========================================
Semantic verdict: FAIL
Headline: Runtime evidence consistency checks failed.

Open these in order:
1. u6_field_validation_summary.md
2. u6_field_validation_20260325_172005__semantic_consistency_verdict.txt
3. u6_field_validation_20260325_172005__summary.txt
4. u6_field_validation_20260325_172005__preflight_report.txt
5. u6_field_validation_20260325_172005__events.csv
6. u6_field_validation_20260325_172005__diagnostics.json

Most useful quick facts:
- Mode requested: real
- Mode entered: real
- Disconnect count: 1
- Recovery count: 0
- Stabilization state family: disconnected
```

## Summary excerpt
```text
UDQ U6 Guided Field Validation Summary
=====================================
bundle_dir: C:\Users\iaq16\Documents\Code\uDAQ\UDQ_PKG_20260325_IMPLEMENTATION_ENTRY_OPTIMIZATION_R02_SPRINT3A_GUIDED_FIELD_VALIDATION\proof\field_tests\u6_field_validation_20260325_172005
mode_requested: real
mode_entered: real
serial_number: AUTO
capture_count: 4
semantic_verdict: FAIL
semantic_verdict_reason: Runtime evidence consistency checks failed.

Session Inventory
-----------------
discovered_support_pack_device_count: 3
- generic_adapter_inventory:SIM-READ-001: SIM-READ-001 (provider=generic_adapter_inventory, serial=)
- generic_adapter_inventory:SIM-WRITE-001: SIM-WRITE-001 (provider=generic_adapter_inventory, serial=)
- labjack_u6_support:360022207: LabJack U6 (360022207) (provider=labjack_u6_support, serial=360022207)

Incident Summary
----------------
disconnect_count: 1
recovery_count: 0
session_had_disconnect: True
session_recovered_after_disconnect: False
last_disconnect_at: 131
last_disconnect_reason: real LabJack U6 backend init failed: Device no longer connected
last_recovery_at: None
last_recovery_reason: None

Recovery Analysis
-----------------
reconnect_attempt_started: True
backend_reopen_observed: True
active_adapter_rebound_observed: False
post_disconnect_successful_poll_observed: False
recovered: False
recovery_stage: backend_reopen_failed
stabilization_state_family: disconnected
last_recovery_failure_stage: backend_reopen_failed
last_recovery_failure_reason: real LabJack U6 backend init failed: Device no longer connected

Phase Timeline
--------------
- baseline: status=PASS observed=live / ready / healthy (family=live_ready_healthy) expected=live / ready / healthy
- device_loss_window: status=FAIL observed=pre-run / configure (family=configuration_pre_run) expected=disconnected
- recovery_window: status=FAIL observed=disconnected (family=disconnected) expected=recovering
- post_recovery_stabilization: status=FAIL observed=disconnected (family=disconnected) expected=live / ready / healthy

Reviewer Runtime Rollup
-----------------------
state_family: disconnected
reviewer_label: disconnected
summary: Runtime posture is disconnected; alarms=0, disconnects=1, recoveries=0.

Canonical Runtime Evidence Bundle
---------------------------------
bundle_version: v1
recent_runtime_event_count: 16
recent_alarm_event_count: 0
recent_operator_action_count: 0

Semantic Consistency Checks
---------------------------
- PASS: rollup_matches_canonical_state — rollup state family `disconnected` matches canonical runtime state family.
- PASS: reviewer_summary_matches_canonical_bundle — reviewer summary matches the canonical bundle renderer.
- PASS: final_phase_matches_rollup — final phase posture matches the reviewer rollup state family.
- FAIL: phase_expectations_hold — one or more strict phase expectations failed: device_loss_window, recovery_window, post_recovery_stabilization.
- PASS: operator_markers_are_distinct — operator and harness markers remain distinct from runtime event rows.
- FAIL: disconnect_has_runtime_evidence — disconnect count is nonzero but no disconnect-class evidence was found in runtime rows or phase records.
- PASS: recovery_has_runtime_evidence — no recovery evidence was required for this run.
- PASS: phase_records_complete — required phase records are present.
- PASS: real_mode_disconnect_observed — real hardware disconnect window produced an observable disturbance.
- FAIL: real_mode_stabilization_observed — real hardware stabilization did not return to the healthy live family.

Output Files
------------
START_HERE__U6_FIELD_VALIDATION.txt
u6_field_validation_20260325_172005__summary.txt
u6_field_validation_summary.md
u6_field_validation_20260325_172005__preflight_report.json
u6_field_validation_20260325_172005__preflight_report.txt
u6_field_validation_20260325_172005__events.csv
u6_field_validation_20260325_172005__diagnostics.json
u6_field_validation_20260325_172005__semantic_consistency_verdict.json
u6_field_validation_20260325_172005__semantic_consistency_verdict.txt
u6_field_validation_20260325_172005__artifact_manifest.json
u6_field_validation_20260325_172005__artifact_manifest.txt
u6_field_validation_20260325_172005__smoke.txt
```

## Semantic verdict excerpt
```text
UDQ U6 Guided Field Validation — Semantic Consistency Verdict
===========================================================
verdict: FAIL
summary: Runtime evidence consistency checks failed.
check_count: 10
fail_count: 3
advisory_count: 0

Checks
------
- PASS: rollup_matches_canonical_state — rollup state family `disconnected` matches canonical runtime state family.
- PASS: reviewer_summary_matches_canonical_bundle — reviewer summary matches the canonical bundle renderer.
- PASS: final_phase_matches_rollup — final phase posture matches the reviewer rollup state family.
- FAIL: phase_expectations_hold — one or more strict phase expectations failed: device_loss_window, recovery_window, post_recovery_stabilization.
- PASS: operator_markers_are_distinct — operator and harness markers remain distinct from runtime event rows.
- FAIL: disconnect_has_runtime_evidence — disconnect count is nonzero but no disconnect-class evidence was found in runtime rows or phase records.
- PASS: recovery_has_runtime_evidence — no recovery evidence was required for this run.
- PASS: phase_records_complete — required phase records are present.
- PASS: real_mode_disconnect_observed — real hardware disconnect window produced an observable disturbance.
- FAIL: real_mode_stabilization_observed — real hardware stabilization did not return to the healthy live family.
```

## Sprint 03B interpretation
The specimen demonstrates two bounded problems:
1. same-session reconnect did not succeed in the guided real-U6 run,
2. the runtime-evidence layer underrepresented the disconnect incident and allowed live-session device loss to fall back to configuration language.

Sprint 03B addresses those exact defects and requires the same harness rerun for closure.
