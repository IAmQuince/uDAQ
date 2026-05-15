# Acceptance test plan — 20260515_02_mapping

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Required automated tests

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_mapping_sandbox_state.py tests/unit/test_mapping_sandbox_diff.py tests/contract/test_mapping_apply_sandbox_boundary.py tests/contract/test_mapping_apply_rollback.py tests/ui/test_testing_menu_smoke.py tests/contract/test_sprint_mapping_diagnostics.py -q
```

## Required inherited regression tests

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/contract/test_contract_mapping_apply_preflight_review_path.py tests/contract/test_contract_mapping_apply_shell_review_hooks.py tests/contract/test_contract_mapping_apply_dry_run_commit_boundary.py -q
```

## Required package checks

```bash
PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.validate_handoff_package
PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_package_entry_surfaces
PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_readme_control
PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_completeness
PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_classification
PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.validate_active_lane_boundedness
PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.validate_windows_path_budget --package-root . --delivery-root 20260515_02_mapping
```

## Manual user test

Follow `docs/testing/20260515_02_manual-test-checklist.md`.


## R2 hotfix acceptance addendum

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/contract/test_contract_visible_shell_wiring_hotfix.py -q
PYTHONDONTWRITEBYTECODE=1 python -m tools.dev.run_sprint_diagnostics --package-root . --acceptance-only
```

Expected result: visible-shell wiring audit passes and the active shell class has non-stub Logic node callbacks.
