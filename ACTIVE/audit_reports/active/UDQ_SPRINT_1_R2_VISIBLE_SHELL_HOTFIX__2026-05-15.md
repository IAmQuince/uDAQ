# Sprint 1 R2 visible-shell hotfix validation

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`
Status: ACTIVE
Revision: r0
Owner: Core Architecture
Authority: PRIMARY
Source docs: RELEASE_NOTES.md, ACCEPTANCE_TEST_PLAN.md, docs/testing/20260515_02_manual-test-checklist.md

## Defect addressed

The initial Sprint 1 package exposed a visible-shell startup regression from the user entry point. The active `OperatorShellWindow` attempted to wire Logic workspace buttons to callbacks that did not exist on the active class, and workspace-tab refresh could call `_refresh_system_summary()` before `system_summary` was constructed.

## Non-stub fix evidence

- The active shell class now includes `_default_logic_nodes`, `_add_logic_node`, `_remove_last_logic_node`, `_reset_logic_nodes`, `_evaluate_logic_nodes`, `_refresh_logic_watch`, and `_build_logic_demo_scene`.
- `_remove_last_logic_node` mutates the draft/demo logic-node model, refreshes the graphics scene, refreshes the inspector/watch text, and reports explicit empty-state status.
- `_build_logic_demo_scene` renders the current draft-node model and displays a deliberate empty-state message when the draft chain is empty.
- Workspace tab-change wiring is connected only after `_build_system_workspace()` constructs `system_summary`.
- The System Summary refresh still writes meaningful summary content; it was not silenced.

## Added validation

- `tests/contract/test_contract_visible_shell_wiring_hotfix.py`
- `run_visible_shell_wiring_audit()` in `src/universaldaq/testing/sprint_mapping.py`
- `Testing -> Run Visible Shell Wiring Audit`

## Validation results

- R2 visible-shell wiring hotfix tests: `3 passed`
- Sprint 1 focused/hotfix tests: `14 passed`
- Inherited mapping-boundary tests: `12 passed`
- Sprint diagnostic acceptance suite: pass, including Visible Shell Wiring Audit
- Handoff package validator: pass
- README/control validator: pass
- Document completeness validator: pass
- Package entry validator: pass
- Document classification validator: pass
- Document debt validator: pass
- Active-lane boundedness validator: pass
- Windows path-budget validator for `20260515_02_mapping-r2`: pass

## Boundary retained

This hotfix does not add live mapping apply, hardware writes, Modbus, or output authority. The mapping changes remain sandbox-only.
