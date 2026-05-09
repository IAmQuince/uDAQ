# Sprint Time Summary — 20260330_09

- instrumented_command_count: `39`
- total_instrumented_seconds: `385.974`

## Phase totals
- `BASELINE_AUDIT`: `47.824s` (12.4%)
- `PACKAGE_VALIDATION`: `290.704s` (75.3%)
- `TARGETED_VALIDATION`: `47.446s` (12.3%)

## Command rows
- `BASELINE_AUDIT` / `baseline_entry_surfaces`: `4.245s`, exit `0`
- `BASELINE_AUDIT` / `baseline_active_lane`: `2.543s`, exit `1`
- `BASELINE_AUDIT` / `baseline_active_lane_after_archive`: `7.358s`, exit `0`
- `BASELINE_AUDIT` / `baseline_requirement_links`: `6.745s`, exit `0`
- `BASELINE_AUDIT` / `baseline_invariant_links`: `9.357s`, exit `0`
- `BASELINE_AUDIT` / `baseline_shell_smoke`: `17.576s`, exit `0`
- `TARGETED_VALIDATION` / `focused_mapping_apply_preflight_tests_after_syntax_repair`: `12.639s`, exit `0`
- `TARGETED_VALIDATION` / `focused_authoritative_readback_regression_tests`: `16.39s`, exit `0`
- `TARGETED_VALIDATION` / `targeted_shell_smoke_after_preflight_patch`: `7.294s`, exit `0`
- `PACKAGE_VALIDATION` / `package_entry_surfaces_after_docs`: `7.115s`, exit `0`
- `PACKAGE_VALIDATION` / `package_active_lane_after_docs`: `7.512s`, exit `0`
- `PACKAGE_VALIDATION` / `package_requirement_links_after_preflight_tests`: `6.294s`, exit `0`
- `PACKAGE_VALIDATION` / `package_invariant_links_after_preflight_tests`: `5.84s`, exit `0`
- `PACKAGE_VALIDATION` / `package_worked_example_links_after_preflight_tests`: `7.004s`, exit `0`
- `PACKAGE_VALIDATION` / `package_readme_control`: `10.808s`, exit `1`
- `PACKAGE_VALIDATION` / `package_readme_control_after_control_field_repair`: `5.3s`, exit `0`
- `PACKAGE_VALIDATION` / `package_document_debt`: `7.799s`, exit `0`
- `PACKAGE_VALIDATION` / `package_document_classification`: `8.622s`, exit `1`
- `PACKAGE_VALIDATION` / `package_document_classification_after_phrase_repair`: `11.684s`, exit `1`
- `PACKAGE_VALIDATION` / `package_document_classification_after_exact_phrase_repair`: `8.094s`, exit `0`
- `PACKAGE_VALIDATION` / `package_document_impact`: `11.699s`, exit `0`
- `PACKAGE_VALIDATION` / `package_document_completeness`: `6.381s`, exit `0`
- `TARGETED_VALIDATION` / `targeted_core_isolation_support_pack_tests`: `11.123s`, exit `0`
- `PACKAGE_VALIDATION` / `final_active_lane_after_archive`: `10.183s`, exit `0`
- `PACKAGE_VALIDATION` / `final_shell_smoke`: `4.088s`, exit `0`
- `PACKAGE_VALIDATION` / `final_path_budget`: `4.165s`, exit `0`
- `PACKAGE_VALIDATION` / `final_requirement_links`: `6.236s`, exit `0`
- `PACKAGE_VALIDATION` / `final_invariant_links`: `4.815s`, exit `0`
- `PACKAGE_VALIDATION` / `final_worked_example_links`: `3.438s`, exit `0`
- `PACKAGE_VALIDATION` / `final_package_entry_surfaces`: `3.566s`, exit `0`
- `PACKAGE_VALIDATION` / `final_readme_control`: `1.538s`, exit `0`
- `PACKAGE_VALIDATION` / `final_document_classification`: `2.977s`, exit `0`
- `PACKAGE_VALIDATION` / `final_document_debt`: `5.773s`, exit `0`
- `PACKAGE_VALIDATION` / `final_document_impact`: `2.433s`, exit `0`
- `PACKAGE_VALIDATION` / `final_document_completeness`: `2.781s`, exit `0`
- `PACKAGE_VALIDATION` / `final_master_audit`: `4.782s`, exit `2`
- `PACKAGE_VALIDATION` / `final_master_audit_after_arg_repair`: `7.309s`, exit `0`
- `PACKAGE_VALIDATION` / `closeout_full_local_gate_timeout_probe`: `120.0s`, exit `124`
- `PACKAGE_VALIDATION` / `final_active_lane_with_closeout_reports`: `2.468s`, exit `0`

## Non-zero command exits
- `baseline_active_lane` exited `1`
- `package_readme_control` exited `1`
- `package_document_classification` exited `1`
- `package_document_classification_after_phrase_repair` exited `1`
- `final_master_audit` exited `2`
- `closeout_full_local_gate_timeout_probe` exited `124`
