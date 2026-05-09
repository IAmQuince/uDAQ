# Sprint Time Ledger — 20260330_08

This ledger records timed validation and packaging commands for the controller-backed authoritative mapping readback sprint. Manual edit phases are summarized in the release notes and implementation summary.

## baseline-package-entry-surfaces

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T04:35:46+00:00`
- end_utc: `2026-05-07T04:35:51+00:00`
- duration_seconds: `5.014`
- exit_code: `0`
- command: `python -m tools.governance.validate_package_entry_surfaces --package-root .`

## baseline-active-lane-boundedness

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T04:35:58+00:00`
- end_utc: `2026-05-07T04:36:06+00:00`
- duration_seconds: `7.781`
- exit_code: `0`
- command: `python -m tools.package_build.validate_active_lane_boundedness --package-root .`

## baseline-requirement-links

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T04:36:32+00:00`
- end_utc: `2026-05-07T04:36:40+00:00`
- duration_seconds: `8.11`
- exit_code: `0`
- command: `python -m tools.traceability.validate_requirement_links --package-root .`

## baseline-invariant-links

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T04:36:58+00:00`
- end_utc: `2026-05-07T04:37:06+00:00`
- duration_seconds: `8.49`
- exit_code: `0`
- command: `python -m tools.traceability.validate_invariant_links --package-root .`

## baseline-shell-smoke

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T04:37:38+00:00`
- end_utc: `2026-05-07T04:37:49+00:00`
- duration_seconds: `11.008`
- exit_code: `0`
- command: `python -m tools.dev.run_shell_smoke --package-root .`

## focused-binding-readback-and-shell-mapping-tests

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T04:42:30+00:00`
- end_utc: `2026-05-07T04:42:43+00:00`
- duration_seconds: `12.597`
- exit_code: `0`
- command: `env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/contract/test_contract_authoritative_binding_bridge_inventory.py tests/contract/test_contract_shell_views_and_mapping_helpers.py -q`

## focused-controller-readback-integration-test

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T04:44:49+00:00`
- end_utc: `2026-05-07T04:45:01+00:00`
- duration_seconds: `11.511`
- exit_code: `1`
- command: `env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/integration/test_integration_device_discovery_to_shell_viewmodel.py -q`

## focused-controller-readback-integration-test-rerun

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T04:45:25+00:00`
- end_utc: `2026-05-07T04:45:36+00:00`
- duration_seconds: `10.926`
- exit_code: `1`
- command: `env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/integration/test_integration_device_discovery_to_shell_viewmodel.py -q`

## focused-controller-readback-integration-test-rerun-success

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T04:47:26+00:00`
- end_utc: `2026-05-07T04:47:37+00:00`
- duration_seconds: `11.427`
- exit_code: `0`
- command: `timeout 40s env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/integration/test_integration_device_discovery_to_shell_viewmodel.py -q`

## focused-core-isolation-invariants

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T04:47:55+00:00`
- end_utc: `2026-05-07T04:48:06+00:00`
- duration_seconds: `10.663`
- exit_code: `0`
- command: `timeout 60s env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/invariants/test_invariant_no_direct_labjack_imports_in_core.py tests/invariants/test_invariant_no_direct_optional_support_pack_imports_in_core.py tests/invariants/test_invariant_no_vendor_markers_in_core.py -q`

## changed-shell-smoke-after-readback

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T04:50:46+00:00`
- end_utc: `2026-05-07T04:50:58+00:00`
- duration_seconds: `12.104`
- exit_code: `0`
- command: `timeout 80s python -m tools.dev.run_shell_smoke --package-root .`

## package-readiness-entry-surfaces

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:51:57+00:00`
- end_utc: `2026-05-07T04:52:04+00:00`
- duration_seconds: `6.779`
- exit_code: `0`
- command: `timeout 80s python -m tools.governance.validate_package_entry_surfaces --package-root .`

## package-readiness-active-lane

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:52:39+00:00`
- end_utc: `2026-05-07T04:52:49+00:00`
- duration_seconds: `9.994`
- exit_code: `0`
- command: `timeout 80s python -m tools.package_build.validate_active_lane_boundedness --package-root .`

## package-readiness-readme-control

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:53:22+00:00`
- end_utc: `2026-05-07T04:53:31+00:00`
- duration_seconds: `8.186`
- exit_code: `1`
- command: `timeout 100s bash -lc python -m tools.governance.validate_readme_control --package-root .`

## package-readiness-readme-control-rerun

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:56:06+00:00`
- end_utc: `2026-05-07T04:56:12+00:00`
- duration_seconds: `5.399`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_readme_control --package-root .`

## package-readiness-document-debt

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:56:32+00:00`
- end_utc: `2026-05-07T04:56:40+00:00`
- duration_seconds: `7.692`
- exit_code: `0`
- command: `timeout 100s bash -lc python -m tools.governance.validate_document_debt --package-root .`

## package-readiness-document-classification

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:56:47+00:00`
- end_utc: `2026-05-07T04:56:52+00:00`
- duration_seconds: `4.903`
- exit_code: `1`
- command: `timeout 100s bash -lc python -m tools.governance.validate_document_classification --package-root .`

## package-readiness-document-classification-rerun

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:57:46+00:00`
- end_utc: `2026-05-07T04:57:52+00:00`
- duration_seconds: `6.324`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_document_classification --package-root .`

## package-readiness-document-impact

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:58:12+00:00`
- end_utc: `2026-05-07T04:58:21+00:00`
- duration_seconds: `8.694`
- exit_code: `1`
- command: `timeout 100s bash -lc python -m tools.governance.validate_document_impact --package-root .`

## package-readiness-document-impact-rerun

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:58:58+00:00`
- end_utc: `2026-05-07T04:59:03+00:00`
- duration_seconds: `5.208`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_document_impact --package-root .`

## package-readiness-document-completeness

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:59:19+00:00`
- end_utc: `2026-05-07T04:59:26+00:00`
- duration_seconds: `6.518`
- exit_code: `1`
- command: `timeout 100s bash -lc python -m tools.governance.validate_document_completeness --package-root .`

## package-readiness-document-completeness-rerun

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T04:59:58+00:00`
- end_utc: `2026-05-07T05:00:06+00:00`
- duration_seconds: `7.816`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_document_completeness --package-root .`

## package-readiness-requirement-links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:00:23+00:00`
- end_utc: `2026-05-07T05:00:32+00:00`
- duration_seconds: `8.814`
- exit_code: `0`
- command: `timeout 100s bash -lc python -m tools.traceability.validate_requirement_links --package-root .`

## package-readiness-invariant-links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:00:38+00:00`
- end_utc: `2026-05-07T05:00:46+00:00`
- duration_seconds: `8.41`
- exit_code: `0`
- command: `timeout 100s bash -lc python -m tools.traceability.validate_invariant_links --package-root .`

## package-readiness-worked-example-links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:01:04+00:00`
- end_utc: `2026-05-07T05:01:09+00:00`
- duration_seconds: `5.718`
- exit_code: `0`
- command: `timeout 100s python -m tools.traceability.validate_worked_example_links --package-root .`

## focused-aggregate-readback-tests

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T05:01:36+00:00`
- end_utc: `2026-05-07T05:01:43+00:00`
- duration_seconds: `7.326`
- exit_code: `0`
- command: `timeout 90s env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/contract/test_contract_authoritative_binding_bridge_inventory.py tests/contract/test_contract_shell_views_and_mapping_helpers.py tests/integration/test_integration_device_discovery_to_shell_viewmodel.py tests/invariants/test_invariant_no_direct_labjack_imports_in_core.py tests/invariants/test_invariant_no_direct_optional_support_pack_imports_in_core.py tests/invariants/test_invariant_no_vendor_markers_in_core.py -q`

## final-readme-control

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:02:07+00:00`
- end_utc: `2026-05-07T05:02:13+00:00`
- duration_seconds: `5.073`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_readme_control --package-root .`

## final-package-entry-surfaces

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:02:17+00:00`
- end_utc: `2026-05-07T05:02:23+00:00`
- duration_seconds: `5.981`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_package_entry_surfaces --package-root .`

## final-document-debt

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:02:53+00:00`
- end_utc: `2026-05-07T05:02:59+00:00`
- duration_seconds: `5.694`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_document_debt --package-root .`

## final-document-classification

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:03:13+00:00`
- end_utc: `2026-05-07T05:03:20+00:00`
- duration_seconds: `6.24`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_document_classification --package-root .`

## final-document-impact

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:03:25+00:00`
- end_utc: `2026-05-07T05:03:29+00:00`
- duration_seconds: `4.676`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_document_impact --package-root .`

## final-document-completeness

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:04:00+00:00`
- end_utc: `2026-05-07T05:04:06+00:00`
- duration_seconds: `5.805`
- exit_code: `0`
- command: `timeout 100s python -m tools.governance.validate_document_completeness --package-root .`

## final-requirement-links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:04:20+00:00`
- end_utc: `2026-05-07T05:04:26+00:00`
- duration_seconds: `6.2`
- exit_code: `0`
- command: `timeout 100s python -m tools.traceability.validate_requirement_links --package-root .`

## final-invariant-links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:04:32+00:00`
- end_utc: `2026-05-07T05:04:36+00:00`
- duration_seconds: `4.378`
- exit_code: `0`
- command: `timeout 100s python -m tools.traceability.validate_invariant_links --package-root .`

## final-worked-example-links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:05:07+00:00`
- end_utc: `2026-05-07T05:05:12+00:00`
- duration_seconds: `4.897`
- exit_code: `0`
- command: `timeout 100s python -m tools.traceability.validate_worked_example_links --package-root .`

## final-shell-smoke

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:05:15+00:00`
- end_utc: `2026-05-07T05:05:21+00:00`
- duration_seconds: `6.166`
- exit_code: `0`
- command: `timeout 100s python -m tools.dev.run_shell_smoke --package-root .`

## final-windows-path-budget

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:05:35+00:00`
- end_utc: `2026-05-07T05:05:42+00:00`
- duration_seconds: `7.884`
- exit_code: `0`
- command: `timeout 100s python -m tools.package_build.validate_windows_path_budget --package-root . --delivery-root udq_s02b_r01`

## final-master-audit

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:08:07+00:00`
- end_utc: `2026-05-07T05:08:13+00:00`
- duration_seconds: `5.802`
- exit_code: `0`
- command: `timeout 160s python -m tools.audit.run_master_audit --package-root . --profile controller-backed-authoritative-mapping-readback`

## final-active-lane-inventory

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:08:30+00:00`
- end_utc: `2026-05-07T05:08:37+00:00`
- duration_seconds: `7.506`
- exit_code: `0`
- command: `timeout 100s python -m tools.package_build.validate_active_lane_boundedness --package-root . --report-json audit_reports/active/UDQ_ACTIVE_LANE_INVENTORY__2026-05-07_050830.json --report-md audit_reports/active/UDQ_ACTIVE_LANE_INVENTORY__2026-05-07_050830.md`

## final-sprint-time-summary

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:09:08+00:00`
- end_utc: `2026-05-07T05:09:17+00:00`
- duration_seconds: `9.387`
- exit_code: `0`
- command: `timeout 60s python -m tools.dev.sprint_time_summary --package-root .`


## closeout-full-local-gate-attempt

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T05:09:30+00:00`
- end_utc: `2026-05-07T05:13:30+00:00`
- duration_seconds: `240.0`
- exit_code: `124`
- command: `timeout 180s python -m tools.dev.run_local_gate --package-root .`
- notes: Attempted once at closeout. The command did not complete in this execution environment before the outer tool timeout; focused gates are recorded separately and passed.
