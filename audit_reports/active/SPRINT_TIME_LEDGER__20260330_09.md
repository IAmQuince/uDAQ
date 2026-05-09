# Sprint Time Ledger

## baseline_entry_surfaces

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:02:44+00:00`
- end_utc: `2026-05-07T13:02:48+00:00`
- duration_seconds: `4.245`
- exit_code: `0`
- command: `python -m tools.governance.validate_package_entry_surfaces --package-root .`

## baseline_active_lane

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:02:52+00:00`
- end_utc: `2026-05-07T13:02:54+00:00`
- duration_seconds: `2.543`
- exit_code: `1`
- command: `python -m tools.package_build.validate_active_lane_boundedness --package-root .`

## baseline_active_lane_after_archive

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:03:20+00:00`
- end_utc: `2026-05-07T13:03:27+00:00`
- duration_seconds: `7.358`
- exit_code: `0`
- command: `python -m tools.package_build.validate_active_lane_boundedness --package-root .`

## baseline_requirement_links

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:03:29+00:00`
- end_utc: `2026-05-07T13:03:36+00:00`
- duration_seconds: `6.745`
- exit_code: `0`
- command: `python -m tools.traceability.validate_requirement_links --package-root .`

## baseline_invariant_links

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:04:05+00:00`
- end_utc: `2026-05-07T13:04:15+00:00`
- duration_seconds: `9.357`
- exit_code: `0`
- command: `python -m tools.traceability.validate_invariant_links --package-root .`

## baseline_shell_smoke

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:04:39+00:00`
- end_utc: `2026-05-07T13:04:56+00:00`
- duration_seconds: `17.576`
- exit_code: `0`
- command: `python -m tools.dev.run_shell_smoke --package-root .`

## focused_mapping_apply_preflight_tests_after_syntax_repair

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:10:28+00:00`
- end_utc: `2026-05-07T13:10:40+00:00`
- duration_seconds: `12.639`
- exit_code: `0`
- command: `pytest -q tests/contract/test_contract_mapping_apply_preflight_review_path.py tests/contract/test_contract_mapping_apply_shell_review_hooks.py`

## focused_authoritative_readback_regression_tests

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:10:56+00:00`
- end_utc: `2026-05-07T13:11:13+00:00`
- duration_seconds: `16.39`
- exit_code: `0`
- command: `pytest -q tests/contract/test_contract_authoritative_binding_bridge_inventory.py tests/contract/test_contract_shell_views_and_mapping_helpers.py`

## targeted_shell_smoke_after_preflight_patch

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:11:55+00:00`
- end_utc: `2026-05-07T13:12:02+00:00`
- duration_seconds: `7.294`
- exit_code: `0`
- command: `python -m tools.dev.run_shell_smoke --package-root .`

## package_entry_surfaces_after_docs

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:17:28+00:00`
- end_utc: `2026-05-07T13:17:36+00:00`
- duration_seconds: `7.115`
- exit_code: `0`
- command: `python -m tools.governance.validate_package_entry_surfaces --package-root .`

## package_active_lane_after_docs

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:17:59+00:00`
- end_utc: `2026-05-07T13:18:07+00:00`
- duration_seconds: `7.512`
- exit_code: `0`
- command: `python -m tools.package_build.validate_active_lane_boundedness --package-root . --report-json audit_reports/active/UDQ_ACTIVE_LANE_INVENTORY__2026-05-07_060900.json --report-md audit_reports/active/UDQ_ACTIVE_LANE_INVENTORY__2026-05-07_060900.md`

## package_requirement_links_after_preflight_tests

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:18:37+00:00`
- end_utc: `2026-05-07T13:18:43+00:00`
- duration_seconds: `6.294`
- exit_code: `0`
- command: `python -m tools.traceability.validate_requirement_links --package-root .`

## package_invariant_links_after_preflight_tests

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:18:48+00:00`
- end_utc: `2026-05-07T13:18:54+00:00`
- duration_seconds: `5.84`
- exit_code: `0`
- command: `python -m tools.traceability.validate_invariant_links --package-root .`

## package_worked_example_links_after_preflight_tests

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:19:21+00:00`
- end_utc: `2026-05-07T13:19:29+00:00`
- duration_seconds: `7.004`
- exit_code: `0`
- command: `python -m tools.traceability.validate_worked_example_links --package-root .`

## package_readme_control

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:19:47+00:00`
- end_utc: `2026-05-07T13:19:58+00:00`
- duration_seconds: `10.808`
- exit_code: `1`
- command: `python -m tools.governance.validate_readme_control --package-root .`

## package_readme_control_after_control_field_repair

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:20:25+00:00`
- end_utc: `2026-05-07T13:20:31+00:00`
- duration_seconds: `5.3`
- exit_code: `0`
- command: `python -m tools.governance.validate_readme_control --package-root .`

## package_document_debt

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:20:53+00:00`
- end_utc: `2026-05-07T13:21:00+00:00`
- duration_seconds: `7.799`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_debt --package-root .`

## package_document_classification

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:21:40+00:00`
- end_utc: `2026-05-07T13:21:48+00:00`
- duration_seconds: `8.622`
- exit_code: `1`
- command: `python -m tools.governance.validate_document_classification --package-root .`

## package_document_classification_after_phrase_repair

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:22:29+00:00`
- end_utc: `2026-05-07T13:22:41+00:00`
- duration_seconds: `11.684`
- exit_code: `1`
- command: `python -m tools.governance.validate_document_classification --package-root .`

## package_document_classification_after_exact_phrase_repair

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:23:01+00:00`
- end_utc: `2026-05-07T13:23:09+00:00`
- duration_seconds: `8.094`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_classification --package-root .`

## package_document_impact

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:23:31+00:00`
- end_utc: `2026-05-07T13:23:43+00:00`
- duration_seconds: `11.699`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_impact --package-root .`

## package_document_completeness

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:24:16+00:00`
- end_utc: `2026-05-07T13:24:22+00:00`
- duration_seconds: `6.381`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_completeness --package-root .`

## targeted_core_isolation_support_pack_tests

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:24:38+00:00`
- end_utc: `2026-05-07T13:24:49+00:00`
- duration_seconds: `11.123`
- exit_code: `0`
- command: `pytest -q tests/contract/test_contract_labjack_extension_metadata_isolation.py tests/contract/test_contract_optional_support_pack_loader.py tests/contract/test_contract_support_pack_discovery_is_registry_driven.py`

## final_active_lane_after_archive

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:25:23+00:00`
- end_utc: `2026-05-07T13:25:33+00:00`
- duration_seconds: `10.183`
- exit_code: `0`
- command: `python -m tools.package_build.validate_active_lane_boundedness --package-root . --report-json audit_reports/active/UDQ_ACTIVE_LANE_INVENTORY__2026-05-07_061900.json --report-md audit_reports/active/UDQ_ACTIVE_LANE_INVENTORY__2026-05-07_061900.md`

## final_shell_smoke

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:26:17+00:00`
- end_utc: `2026-05-07T13:26:21+00:00`
- duration_seconds: `4.088`
- exit_code: `0`
- command: `python -m tools.dev.run_shell_smoke --package-root .`

## final_path_budget

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:26:23+00:00`
- end_utc: `2026-05-07T13:26:27+00:00`
- duration_seconds: `4.165`
- exit_code: `0`
- command: `python -m tools.package_build.validate_windows_path_budget --package-root . --delivery-root udq_s02b_r01`

## final_requirement_links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:26:43+00:00`
- end_utc: `2026-05-07T13:26:49+00:00`
- duration_seconds: `6.236`
- exit_code: `0`
- command: `python -m tools.traceability.validate_requirement_links --package-root .`

## final_invariant_links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:26:55+00:00`
- end_utc: `2026-05-07T13:27:00+00:00`
- duration_seconds: `4.815`
- exit_code: `0`
- command: `python -m tools.traceability.validate_invariant_links --package-root .`

## final_worked_example_links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:27:03+00:00`
- end_utc: `2026-05-07T13:27:07+00:00`
- duration_seconds: `3.438`
- exit_code: `0`
- command: `python -m tools.traceability.validate_worked_example_links --package-root .`

## final_package_entry_surfaces

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:27:21+00:00`
- end_utc: `2026-05-07T13:27:24+00:00`
- duration_seconds: `3.566`
- exit_code: `0`
- command: `python -m tools.governance.validate_package_entry_surfaces --package-root .`

## final_readme_control

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:27:27+00:00`
- end_utc: `2026-05-07T13:27:29+00:00`
- duration_seconds: `1.538`
- exit_code: `0`
- command: `python -m tools.governance.validate_readme_control --package-root .`

## final_document_classification

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:27:33+00:00`
- end_utc: `2026-05-07T13:27:36+00:00`
- duration_seconds: `2.977`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_classification --package-root .`

## final_document_debt

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:27:46+00:00`
- end_utc: `2026-05-07T13:27:52+00:00`
- duration_seconds: `5.773`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_debt --package-root .`

## final_document_impact

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:27:56+00:00`
- end_utc: `2026-05-07T13:27:58+00:00`
- duration_seconds: `2.433`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_impact --package-root .`

## final_document_completeness

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:28:02+00:00`
- end_utc: `2026-05-07T13:28:05+00:00`
- duration_seconds: `2.781`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_completeness --package-root .`

## final_master_audit

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:28:16+00:00`
- end_utc: `2026-05-07T13:28:21+00:00`
- duration_seconds: `4.782`
- exit_code: `2`
- command: `python -m tools.audit.run_master_audit --package-root . --report-md audit_reports/active/UDQ_MASTER_AUDIT__2026-05-07_062200.md`

## final_master_audit_after_arg_repair

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:28:36+00:00`
- end_utc: `2026-05-07T13:28:44+00:00`
- duration_seconds: `7.309`
- exit_code: `0`
- command: `python -m tools.audit.run_master_audit --package-root .`


## closeout_full_local_gate_timeout_probe

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:29:14+00:00`
- end_utc: `2026-05-07T13:31:14+00:00`
- duration_seconds: `120.0`
- exit_code: `124`
- command: `timeout 120s python -m tools.dev.run_local_gate --package-root .`
- notes: Full local gate reached early validator output and generated a PASS_CLEAN master audit, but the environment timed out before a conclusive complete gate result was captured.
## final_active_lane_with_closeout_reports

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:31:23+00:00`
- end_utc: `2026-05-07T13:31:25+00:00`
- duration_seconds: `2.468`
- exit_code: `0`
- command: `python -m tools.package_build.validate_active_lane_boundedness --package-root . --report-json audit_reports/active/UDQ_ACTIVE_LANE_INVENTORY__2026-05-07_061900.json --report-md audit_reports/active/UDQ_ACTIVE_LANE_INVENTORY__2026-05-07_061900.md`

