# Tests and Tools

**Controlled document**  
ID: UDQ-HANDBOOK-TESTS-001  
Status: ACTIVE  
Revision: r16  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-GOV-REG-003, UDQ-GOV-LOG-001, UDQ-SPRINT-SOP-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Package identity

- Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`
- Package status: Sprint 1 mapping sandbox mutation proof
- Runtime behavior changes: sandbox-only mapping state mutation implemented

## Sprint 1 required tools

Run from `ACTIVE/`:

- `PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.validate_handoff_package`
- `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_readme_control --package-root .`
- `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_completeness --package-root .`
- `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_package_entry_surfaces --package-root .`
- `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_classification --package-root .`
- `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_debt --package-root .`
- `PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.validate_active_lane_boundedness --package-root .`
- `PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.validate_windows_path_budget --package-root . --delivery-root 20260515_02_mapping`

## Focused inherited-behavior sanity checks

Sprint 1 requires the focused sandbox tests plus inherited mapping-boundary regression checks. Hardware-in-loop tests are not required because live apply and physical outputs remain deferred. The inherited regression check is:

```bash
python -m pytest   tests/contract/test_contract_mapping_apply_preflight_review_path.py   tests/contract/test_contract_mapping_apply_shell_review_hooks.py   tests/contract/test_contract_mapping_apply_dry_run_commit_boundary.py   -q
```

## Generated-artifact hygiene

Use `PYTHONDONTWRITEBYTECODE=1` for validation runs or run `python -m tools.package_build.clean_generated_artifacts` before final packaging. Python cache directories are not package content.

## Tool classification

- Package gates: handoff package validation, package entry, readme control, document completeness, classification, active-lane boundedness, path budget.
- Changed-area gates: targeted unit/contract/acceptance tests selected by the sprint plan.
- Advisory diagnostics: inventory dumps and capability reports that inform debugging but are not always release blockers.
- Hardware-in-loop gates: required only for sprints that claim real-device behavior.

## Sprint 1 changed-area tests

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_mapping_sandbox_state.py tests/unit/test_mapping_sandbox_diff.py tests/contract/test_mapping_apply_sandbox_boundary.py tests/contract/test_mapping_apply_rollback.py tests/ui/test_testing_menu_smoke.py tests/contract/test_sprint_mapping_diagnostics.py -q
```

## User-facing diagnostic launcher

Run `RUN_DIAGNOSTICS.bat` from `ACTIVE/` to generate `diagnostics/20260515_02_diagnostic-bundle.zip`.
