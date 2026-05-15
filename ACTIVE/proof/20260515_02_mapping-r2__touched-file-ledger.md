# Sprint 1 R2 touched-file ledger

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Source files changed

- `src/universaldaq/ui/qt_shell.py` — restored active-shell Logic workspace callbacks and moved workspace-tab refresh wiring after System workspace construction.
- `src/universaldaq/ui/visible_shell.py` — added `Testing -> Run Visible Shell Wiring Audit`.
- `src/universaldaq/testing/sprint_mapping.py` — added visible-shell wiring audit to user-runnable diagnostics and sprint acceptance suite.
- `src/universaldaq/testing/__init__.py` — exported the new audit runner.

## Test files added

- `tests/contract/test_contract_visible_shell_wiring_hotfix.py`

## Documentation and release files changed

- `CHANGELOG.md`
- `ACCEPTANCE_TEST_PLAN.md`
- `PACKAGE_MANIFEST.md`
- `ROOT_PACKAGE_INDEX.md`
- `config/package_metadata.json`
- `docs/release/RELEASE_NOTES.md`
- `docs/release/RELEASE_MANIFEST.yaml`
- `docs/release/20260515_02_mapping__validation-summary.md`
- `docs/testing/20260515_02_manual-test-checklist.md`
- Package-ID surfaces updated from `UDQ-PKG-20260515-02-MAPPING-R01` to `UDQ-PKG-20260515-02-MAPPING-R02`.

## Generated validation artifacts

- `audit_reports/active/UDQ_SPRINT_1_R2_VISIBLE_SHELL_HOTFIX__2026-05-15.md`
- `audit_reports/testing/20260515_02_visible-shell-wiring-audit.json`
- `audit_reports/testing/20260515_02_sprint-acceptance-suite.json`
