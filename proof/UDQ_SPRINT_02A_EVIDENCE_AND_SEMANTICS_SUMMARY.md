# Sprint 2A — U6 Evidence and Semantics Cleanup Summary

## Scope
This pass tightened the U6 evidence layer after the first real-hardware field-test review.

It did **not** widen the platform scope. It stayed focused on:
- disconnect/recovery accounting semantics,
- runtime event surfacing,
- lifecycle vocabulary consistency in the field-test bundle,
- forensic failure/recovery retention,
- and Windows-safe package delivery discipline.

## Main changes
- corrected real-U6 incident accounting so a runtime loss is counted as one disconnect incident rather than as repeated retry failures
- added recovery counting and retained disconnect/recovery timestamps and reasons in the U6 status snapshot
- preserved session-level forensic truth (`session_had_disconnect`, `session_recovered_after_disconnect`) after recovery
- surfaced recent runtime-event rows in the lifecycle review bundle
- improved the field-test bundle summary, event CSV, and diagnostics JSON with incident summary and lifecycle vocabulary context
- added package-build support for short delivery roots and Windows path-budget validation
- kept cache and bytecode exclusions in the package builder and validated delivery-shape safety explicitly

## Verification completed in this pass
- `python -m tools.package_build.validate_windows_path_budget --package-root . --delivery-root udq_s02b_r01` → PASS
- `python -m tools.governance.validate_package_entry_surfaces --package-root .` → PASS
- `python -m tools.governance.validate_document_completeness --package-root .` → PASS
- `python -m tools.dev.run_shell_smoke --package-root .` → PASS
- `python -m tools.dev.run_labjack_u6_smoke --package-root .` → PASS
- `python -m tools.audit.run_master_audit --package-root . --profile sprint-02-u6-bounded-hardening` → PASS
- `pytest -q -p no:cacheprovider tests/meta` → 29 passed
- `pytest -q -p no:cacheprovider tests/contract` → 43 passed
- `pytest -q -p no:cacheprovider tests/scenario` → 25 passed
- `pytest -q -p no:cacheprovider tests/invariants tests/integration tests/regression` → 52 passed

## Important limitation
This pass did **not** include a second real-hardware rerun inside the package workspace.

The updated disconnect/recovery semantics, runtime-event rows, and improved bundle output are therefore code-verified and test-verified here, but they still need to be rechecked on your physical U6 with the updated field-test harness.

## Recommended next action
Run the same physical U6 field-test sequence again with:
- `tools\dev\run_u6_field_test_harness.bat`

Then return the generated bundle directory from:
- `proof\field_tests\u6_field_test_bundle_...`
