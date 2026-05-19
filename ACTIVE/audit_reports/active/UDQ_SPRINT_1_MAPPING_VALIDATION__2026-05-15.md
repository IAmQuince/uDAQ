# Sprint 1 mapping validation report

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Focused tests

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_mapping_sandbox_state.py tests/unit/test_mapping_sandbox_diff.py tests/contract/test_mapping_apply_sandbox_boundary.py tests/contract/test_mapping_apply_rollback.py tests/ui/test_testing_menu_smoke.py tests/contract/test_sprint_mapping_diagnostics.py -q
```

Observed result during package preparation: `11 passed`.

## Inherited mapping-boundary regression

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/contract/test_contract_mapping_apply_preflight_review_path.py tests/contract/test_contract_mapping_apply_shell_review_hooks.py tests/contract/test_contract_mapping_apply_dry_run_commit_boundary.py -q
```

Observed result during package preparation: `12 passed`.

## Governance/package checks

Observed passes during package preparation:

- handoff package validation
- package entry validation
- readme control validation
- document completeness validation
- document classification validation
- document debt validation
- active-lane boundedness validation
- Windows path-budget validation

## User diagnostic entry

`RUN_DIAGNOSTICS.bat` is backed by `tools/dev/run_sprint_diagnostics.py` and produces `diagnostics/20260515_02_diagnostic-bundle.zip`.
