# Package manifest — 20260515_02_mapping-r2

**CANONICAL CURRENT ENTRY DOCUMENT**

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`  
Package status: ACTIVE Sprint 1 mapping sandbox mutation proof  
Root folder: `20260515_02_mapping-r2`

## Primary contents

| Path | Purpose |
|---|---|
| `RUN_UDAQ.bat` | User-facing visible shell launcher |
| `RUN_DIAGNOSTICS.bat` | No-hardware diagnostic bundle launcher |
| `README_START_HERE.md` | Canonical current entry point |
| `docs/testing/20260515_02_manual-test-checklist.md` | Manual user test checklist |
| `src/universaldaq/mapping/sandbox.py` | Sandbox-only mapping state, apply, rollback, and diff implementation |
| `src/universaldaq/testing/sprint_mapping.py` | User-runnable Sprint 1 diagnostic/acceptance harness |
| `tests/unit/test_mapping_sandbox_state.py` | Sandbox state unit tests |
| `tests/unit/test_mapping_sandbox_diff.py` | Diff/report unit tests |
| `tests/contract/test_mapping_apply_sandbox_boundary.py` | Sandbox-only mutation boundary tests |
| `tests/contract/test_mapping_apply_rollback.py` | Rollback contract tests |
| `tests/ui/test_testing_menu_smoke.py` | Testing menu presence smoke test |
| `audit_reports/testing/` | Generated user-test reports |
| `diagnostics/` | Generated diagnostic bundles |

## Boundary statement

Sprint 1 implements sandbox mutation only. Live mapping apply, real hardware writes, output authority, and physical command execution remain deferred.
