# Cursor first-pass engineering status — 2026-05-16

**Controlled release companion document**  
ID: UDQ-REL-CURSOR-FIRST-PASS-20260516-00  
Status: REVIEW  
Revision: r0  
Owner: External Engineering Review  
Authority: DERIVED  
Source docs: UDQ-README-ROOT-001, UDQ-HANDBOOK-START-001, UDQ-HANDBOOK-NEXT-001, UDQ-REL-REVIEW-START-20260515-002, UDQ-REL-NOTES-20260515-002  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## 1. Current package identity

- Project package name from `pyproject.toml`: `universaldaq`
- Project version from `pyproject.toml`: `0.1.0`
- Formal package identity: `UDQ-PKG-20260515-02-MAPPING-R02`
- Package date: `2026-05-15`
- Controlled README revision: `r36`
- Current review entry revision: `r1`
- Current branch at review: `cursor/first-pass-status-229a`
- Current commit at review start: `ccbc650715c37e6d29dee4d64369cc7cde7fa7a9`
- Repository root: `/workspace`
- Actual Python package root: `/workspace/ACTIVE`
- `ACTIVE/` status: present and authoritative for the current Python package.
- Root-layout finding: repository root contains `ACTIVE/`, `HISTORICAL/`, `ROOT_PACKAGE_INDEX.md`, and root `README.md`; `pyproject.toml` is under `ACTIVE/`, not the visible repository root.
- Security entrypoint finding: no `SECURITY.md` was present at repository root or `ACTIVE/`; the active security baseline is `docs/active/UDQ-SEC-BASELINE-001__Security_and_Trust_Boundary_Baseline__r0__WIP.md`.

## 2. What currently works

- Editable install from `ACTIVE/` with `python3 -m pip install -e ".[ui,dev]"` completed successfully under Python 3.12.3.
- Import smoke passed for `universaldaq`, `universaldaq_labjack`, `universaldaq_arduino`, and `universaldaq_rpi`.
- Shell smoke passed in simulated/headless mode with four detected demo devices and denied output authority.
- Simulated LabJack U6 smoke passed without real hardware.
- Sprint mapping acceptance diagnostics passed, including smoke, sandbox apply, rollback, diff report, and visible-shell wiring audit.
- Focused mapping tests passed: 18 passed across sandbox state, diff, apply boundary, rollback, preflight/review, and dry-run commit boundary.
- Installed console script `udq-shell-smoke` works when `PYTHONPATH=.` is supplied from `ACTIVE/`.

## 3. What currently does not work

### Pytest and governance

Full pytest is not clean: `266 passed, 9 failed`.

Failing tests observed:

1. `tests/invariants/test_invariant_no_vendor_markers_in_core.py::test_universal_core_contains_no_vendor_markers_in_python_modules`
   - `src/universaldaq/mapping/sandbox.py` contains demo endpoint/vendor markers such as `AIN1`.
2. `tests/meta/test_meta_controller_decomposition.py::test_controller_concentration_reduced_and_handlers_exist`
   - `src/universaldaq/app/controller.py` has 1125 lines; threshold is less than 950.
3. `tests/meta/test_meta_documentation_impact_rules.py::test_documentation_impact_validator_passes`
   - `docs/handbook/IMPLEMENTATION_ENTRY.md` is missing required phrases: `phase 0`, `phase 4`, `save point`.
   - `docs/handbook/NEXT_ACTIONS.md` is missing required phrases: `reconciliation`, `phase 3`.
   - `README.md` is missing required phrases: `save-point reconciliation baseline`, `still intentionally deferred`.
4. `tests/meta/test_meta_invariant_references.py::test_all_referenced_invariants_exist`
   - `tests/contract/test_mapping_apply_rollback.py` lacks `TEST_DECLARATION`.
5. `tests/meta/test_meta_no_archived_reference_ids.py::test_test_declarations_do_not_reference_archive_paths`
   - blocked by the missing `TEST_DECLARATION` in `tests/contract/test_mapping_apply_rollback.py`.
6. `tests/meta/test_meta_package_entry_surfaces.py::test_package_entry_assets_exist`
   - `PACKAGE_ENTRY_REGISTRY.yaml` has canonical role `active_review`; the test expects canonical role `review_entry`.
7. `tests/meta/test_meta_pass2_reviewer_guide_present.py::test_legacy_pass2_hardening_guide_is_retained_for_traceability`
   - `docs/release/history/PASS2_REVIEW_HARDENING_SUMMARY__2026-03-23.md` is absent.
8. `tests/meta/test_meta_requirement_references.py::test_all_referenced_requirements_exist`
   - blocked by the missing `TEST_DECLARATION` in `tests/contract/test_mapping_apply_rollback.py`.
9. `tests/meta/test_meta_root_layer_allowlist.py::test_root_layer_contains_only_allowed_front_door_entries`
   - active package root contains front-door files not listed in the meta-test allowlist, including `ACCEPTANCE_TEST_PLAN.md`, `CHANGELOG.md`, `FEATURE_INVENTORY.md`, `KNOWN_LIMITATIONS.md`, `PACKAGE_MANIFEST.md`, and `README_START_HERE.md`.

Meta-only pytest is not clean: `24 passed, 8 failed`.

Aggregate local gate is not clean: `python3 -m tools.dev.run_local_gate --package-root .` stops in `tools.audit.run_master_audit` on the missing `TEST_DECLARATION` in `tests/contract/test_mapping_apply_rollback.py`.

### Lint, format, and type diagnostics

Ruff check is not clean: 518 errors.

- `I001` unsorted imports: 167
- `UP037` quoted annotations: 97
- `E702` multiple statements on one line: 62
- `UP035` deprecated imports: 55
- `E402` imports not at top of file: 52
- `F401` unused imports: 36
- `UP017` datetime timezone UTC: 18
- `B009` constant `getattr`: 8
- `UP006` non-PEP585 annotations: 6
- `F841` unused variables: 5
- Other single-digit categories include `E401`, `B008`, invalid syntax, `B018`, `B905`, `F541`, `F811`, and `F821`.

Ruff format check is not clean: 416 files would be reformatted and 35 files are already formatted.

Mypy is not clean: 1205 errors in 109 files across 451 checked source files.

- `attr-defined`: 354
- `index`: 335
- `arg-type`: 138
- `call-overload`: 88
- `no-untyped-def`: 85
- `union-attr`: 70
- `operator`: 30
- `no-any-return`: 26
- `assignment`: 26
- Additional categories include `dict-item`, `var-annotated`, `type-arg`, `return-value`, `list-item`, `unused-ignore`, `misc`, `import-untyped`, `has-type`, `no-redef`, and `used-before-def`.

### Packaging and command-entry drift

- `python` is not available on PATH in this Linux environment; `python3` is required.
- Installed console scripts that import `tools.*` fail without `PYTHONPATH=.` because package discovery is limited to `src`.
- Module commands run cleanly from `ACTIVE/`, so this is packaging/path hygiene rather than a core runtime failure.

## 4. Risk classification

### Release-blocking governance failures

- Missing `TEST_DECLARATION` blocks multiple traceability/meta tests.
- Package entry registry role drift prevents review-entry validation.
- Retained pass2 hardening guide traceability file is absent.
- Documentation impact validator finds required phrases missing in active controlled documents.
- Root-layer allowlist is stale relative to the active package layout.

### Core architecture risks

- Controller concentration remains above the decomposition threshold.
- The active codebase is functionally alive but not governance-clean enough to safely start broad feature work.

### Safety/control-boundary risks

- The tested mapping path remains sandbox-only, rollback-capable, and non-live.
- No tested command introduced live hardware mutation or output authority.
- The main risk is not observed unsafe behavior; it is governance debt around proving and preserving the control boundary.

### Device-abstraction risks

- A vendor-marker invariant fails because core sandbox demo data uses hardware-shaped endpoint names.
- Support packs are present outside `universaldaq` core, but the core marker invariant should be resolved before expanding device work.

### UI/headless-environment limitations

- UI dependencies installed successfully.
- No GUI launch/manual display validation was performed in this pass because the requested scope was command/environment verification and no UI code was changed.
- Visible-shell wiring audit passed through the sprint diagnostics.

### Lint/type debt

- Ruff, format, and mypy all have substantial pre-existing baseline debt.
- These diagnostics should be classified and baselined before applying a no-new-debt rule to touched files.

### Documentation drift

- `SECURITY.md` is absent even though a controlled security baseline document exists.
- Some root/ACTIVE wording is correct, but tool entry points still rely on contributors knowing to work from `ACTIVE/` and sometimes adding `PYTHONPATH=.`

### Packaging/GitHub hygiene issues

- `pyproject.toml` is in `ACTIVE/`, so GitHub repository root is not the Python package root.
- Console-script entry points fail when executed from the installed script alone because `tools` is not installed as a package.

## 5. Interpretation

- Functionally alive: yes. Install, imports, shell smoke, simulated LabJack smoke, focused mapping tests, and sprint acceptance diagnostics all pass.
- Governance-clean: no. Full pytest and meta-only pytest have governance/meta failures.
- Lint-clean: no. Ruff reports 518 errors.
- Format-clean: no. Ruff format would reformat 416 files.
- Type-clean: no. Mypy reports 1205 errors in 109 files.
- UI-verified: partially. Automated visible-shell wiring audit passed; manual GUI launch was not exercised in this first pass.
- Ready for next feature sprint: not yet. The safest next move is a stabilization sprint focused on root/package reconciliation, governance closure, and debt baselining before controller-authorized mapping apply or expanded UI/device work.
