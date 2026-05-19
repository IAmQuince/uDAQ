# Sprint Time Ledger

## baseline-package-entry-surfaces

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:39:08+00:00`
- end_utc: `2026-05-07T13:39:17+00:00`
- duration_seconds: `9.204`
- exit_code: `0`
- command: `python -m tools.governance.validate_package_entry_surfaces --package-root .`

## baseline-active-lane-boundedness

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:39:24+00:00`
- end_utc: `2026-05-07T13:39:30+00:00`
- duration_seconds: `6.078`
- exit_code: `1`
- command: `python -m tools.package_build.validate_active_lane_boundedness --package-root .`

## baseline-active-lane-boundedness-after-archive

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:41:37+00:00`
- end_utc: `2026-05-07T13:41:44+00:00`
- duration_seconds: `7.51`
- exit_code: `0`
- command: `python -m tools.package_build.validate_active_lane_boundedness --package-root .`
- notes: archived sprint09 active artifacts after initial active lane boundedness failure

## baseline-requirement-links

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:42:19+00:00`
- end_utc: `2026-05-07T13:42:28+00:00`
- duration_seconds: `8.469`
- exit_code: `0`
- command: `python -m tools.traceability.validate_requirement_links --package-root .`

## baseline-requirement-links

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:43:37+00:00`
- end_utc: `2026-05-07T13:43:51+00:00`
- duration_seconds: `13.898`
- exit_code: `0`
- command: `python -m tools.traceability.validate_requirement_links --package-root .`

## baseline-invariant-links

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:44:12+00:00`
- end_utc: `2026-05-07T13:44:18+00:00`
- duration_seconds: `5.722`
- exit_code: `0`
- command: `python -m tools.traceability.validate_invariant_links --package-root .`

## baseline-shell-smoke

- phase: `BASELINE_AUDIT`
- start_utc: `2026-05-07T13:44:28+00:00`
- end_utc: `2026-05-07T13:44:35+00:00`
- duration_seconds: `7.218`
- exit_code: `0`
- command: `python -m tools.dev.run_shell_smoke --package-root .`

## targeted-dry-run-commit-boundary-tests

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:48:26+00:00`
- end_utc: `2026-05-07T13:48:43+00:00`
- duration_seconds: `16.514`
- exit_code: `0`
- command: `python -m pytest tests/contract/test_contract_mapping_apply_dry_run_commit_boundary.py -q`

## targeted-sprint08-09-regression-tests

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:49:04+00:00`
- end_utc: `2026-05-07T13:49:20+00:00`
- duration_seconds: `16.332`
- exit_code: `0`
- command: `python -m pytest tests/contract/test_contract_authoritative_binding_bridge_inventory.py tests/contract/test_contract_mapping_apply_preflight_review_path.py tests/contract/test_contract_mapping_apply_shell_review_hooks.py -q`

## targeted-application-import-smoke

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:55:31+00:00`
- end_utc: `2026-05-07T13:55:39+00:00`
- duration_seconds: `8.416`
- exit_code: `1`
- command: `python -`

## targeted-application-import-smoke-with-src-path

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:56:04+00:00`
- end_utc: `2026-05-07T13:56:11+00:00`
- duration_seconds: `7.363`
- exit_code: `0`
- command: `python -c import sys; sys.path.insert(0,'src'); from universaldaq.app import MappingApplyCoordinator, MappingApplyResult, MappingApplyAuditEvent, MappingDryRunCommitState, ShellController; from universaldaq.ui.shell_views import MappingApplyWorkflowState; print('import-ok', MappingDryRunCommitState.ACCEPTED.value, MappingApplyWorkflowState.CONTROLLER_DRY_RUN_ACCEPTED.value)`
- notes: rerun after import smoke failed without PYTHONPATH/src path

## targeted-final-focused-commit-readback-preflight-tests

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:56:32+00:00`
- end_utc: `2026-05-07T13:56:49+00:00`
- duration_seconds: `16.203`
- exit_code: `0`
- command: `python -m pytest tests/contract/test_contract_mapping_apply_dry_run_commit_boundary.py tests/contract/test_contract_authoritative_binding_bridge_inventory.py tests/contract/test_contract_mapping_apply_preflight_review_path.py tests/contract/test_contract_mapping_apply_shell_review_hooks.py -q`

## targeted-core-isolation-invariants

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:57:15+00:00`
- end_utc: `2026-05-07T13:57:28+00:00`
- duration_seconds: `13.339`
- exit_code: `0`
- command: `python -m pytest tests/invariants/test_invariant_no_direct_labjack_imports_in_core.py tests/invariants/test_invariant_no_direct_optional_support_pack_imports_in_core.py tests/invariants/test_invariant_missing_support_pack_dependency_does_not_break_core_startup.py -q`

## targeted-shell-smoke-after-sprint10

- phase: `TARGETED_VALIDATION`
- start_utc: `2026-05-07T13:57:46+00:00`
- end_utc: `2026-05-07T13:58:00+00:00`
- duration_seconds: `13.989`
- exit_code: `0`
- command: `python -m tools.dev.run_shell_smoke --package-root .`

## package-readme-control

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:58:23+00:00`
- end_utc: `2026-05-07T13:58:32+00:00`
- duration_seconds: `9.0`
- exit_code: `0`
- command: `python -m tools.governance.validate_readme_control --package-root .`

## package-entry-surfaces

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T13:59:02+00:00`
- end_utc: `2026-05-07T13:59:12+00:00`
- duration_seconds: `9.898`
- exit_code: `1`
- command: `python -m tools.governance.validate_package_entry_surfaces --package-root .`

## package-entry-surfaces

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:00:01+00:00`
- end_utc: `2026-05-07T14:00:07+00:00`
- duration_seconds: `5.808`
- exit_code: `0`
- command: `python -m tools.governance.validate_package_entry_surfaces --package-root .`

## package-document-debt

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:00:13+00:00`
- end_utc: `2026-05-07T14:00:20+00:00`
- duration_seconds: `6.965`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_debt --package-root .`

## package-document-classification

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:00:43+00:00`
- end_utc: `2026-05-07T14:00:48+00:00`
- duration_seconds: `4.977`
- exit_code: `1`
- command: `python -m tools.governance.validate_document_classification --package-root .`

## package-document-classification-after-phrase-fix

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:01:28+00:00`
- end_utc: `2026-05-07T14:01:33+00:00`
- duration_seconds: `5.504`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_classification --package-root .`
- notes: fixed exact lowercase legacy WIP classification phrase required by validator

## package-document-impact

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:01:51+00:00`
- end_utc: `2026-05-07T14:02:00+00:00`
- duration_seconds: `8.995`
- exit_code: `1`
- command: `python -m tools.governance.validate_document_impact --package-root .`

## package-document-impact-after-phase0-fix

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:02:23+00:00`
- end_utc: `2026-05-07T14:02:33+00:00`
- duration_seconds: `9.697`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_impact --package-root .`
- notes: restored required phase 0 phrase in implementation entry after sprint rewrite

## package-document-completeness

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:02:49+00:00`
- end_utc: `2026-05-07T14:02:58+00:00`
- duration_seconds: `9.868`
- exit_code: `0`
- command: `python -m tools.governance.validate_document_completeness --package-root .`

## package-active-lane-boundedness

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:03:20+00:00`
- end_utc: `2026-05-07T14:03:25+00:00`
- duration_seconds: `5.303`
- exit_code: `0`
- command: `python -m tools.package_build.validate_active_lane_boundedness --package-root .`

## package-requirement-links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:03:51+00:00`
- end_utc: `2026-05-07T14:03:57+00:00`
- duration_seconds: `5.986`
- exit_code: `0`
- command: `python -m tools.traceability.validate_requirement_links --package-root .`

## package-invariant-links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:04:03+00:00`
- end_utc: `2026-05-07T14:04:11+00:00`
- duration_seconds: `7.206`
- exit_code: `0`
- command: `python -m tools.traceability.validate_invariant_links --package-root .`

## package-worked-example-links

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:04:28+00:00`
- end_utc: `2026-05-07T14:04:36+00:00`
- duration_seconds: `7.511`
- exit_code: `0`
- command: `python -m tools.traceability.validate_worked_example_links --package-root .`

## package-shell-smoke-final

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:04:50+00:00`
- end_utc: `2026-05-07T14:04:55+00:00`
- duration_seconds: `4.42`
- exit_code: `0`
- command: `python -m tools.dev.run_shell_smoke --package-root .`

## package-windows-path-budget

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:05:01+00:00`
- end_utc: `2026-05-07T14:05:03+00:00`
- duration_seconds: `2.463`
- exit_code: `0`
- command: `python -m tools.package_build.validate_windows_path_budget --package-root . --delivery-root udq_s02b_r01`

## package-master-audit

- phase: `PACKAGE_VALIDATION`
- start_utc: `2026-05-07T14:05:23+00:00`
- end_utc: `2026-05-07T14:05:30+00:00`
- duration_seconds: `7.127`
- exit_code: `0`
- command: `python -m tools.audit.run_master_audit --package-root .`

