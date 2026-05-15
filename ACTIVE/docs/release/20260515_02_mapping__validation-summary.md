# Sprint 1 validation summary

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Focused Sprint 1 tests

- `tests/unit/test_mapping_sandbox_state.py`
- `tests/unit/test_mapping_sandbox_diff.py`
- `tests/contract/test_mapping_apply_sandbox_boundary.py`
- `tests/contract/test_mapping_apply_rollback.py`
- `tests/ui/test_testing_menu_smoke.py`
- `tests/contract/test_sprint_mapping_diagnostics.py`

Result: `11 passed` during package preparation.

## Inherited mapping-boundary regression tests

- `tests/contract/test_contract_mapping_apply_preflight_review_path.py`
- `tests/contract/test_contract_mapping_apply_shell_review_hooks.py`
- `tests/contract/test_contract_mapping_apply_dry_run_commit_boundary.py`

Result: `12 passed` during package preparation.

## User diagnostic entry point

`RUN_DIAGNOSTICS.bat` runs the Sprint 1 acceptance harness and exports `ACTIVE/diagnostics/20260515_02_diagnostic-bundle.zip`.


## R2 visible-shell hotfix validation

Added and ran `tests/contract/test_contract_visible_shell_wiring_hotfix.py`. Result: `3 passed`.

The Sprint acceptance diagnostic now also runs `Visible Shell Wiring Audit`, which checks that the active `OperatorShellWindow` has real Logic workspace callbacks, that the remove-node action is not a no-op stub, that the System workspace is built before tab-change refresh wiring, and that System Summary refresh writes meaningful content.
