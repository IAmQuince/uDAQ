# Next-sprint recommendation — 2026-05-16

**Controlled release companion document**  
ID: UDQ-REL-NEXT-SPRINT-REC-20260516-00  
Status: REVIEW  
Revision: r0  
Owner: External Engineering Review  
Authority: DERIVED  
Source docs: UDQ-HANDBOOK-NEXT-001, UDQ-REL-CURSOR-FIRST-PASS-20260516-00, UDQ-ROADMAP-SPEC-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Document choice

This recommendation is a dated release companion rather than a direct rewrite of `docs/handbook/NEXT_ACTIONS.md` because `NEXT_ACTIONS.md` is the canonical controlled handbook entry. The companion keeps the first-pass recommendation reviewable without overwriting the active controlled handoff.

## Recommended staged sprint path

### Phase 0 — Root/package reconciliation

Resolve contributor ambiguity between repository root and Python package root.

- Confirm `ACTIVE/` remains the actual package root while repository root remains the delivery/root-lane container.
- Align root `README.md`, `ACTIVE/README.md`, `CONTRIBUTING.md`, local-gate instructions, and any future `AGENTS.md` with the same working-directory rule.
- Document when `PYTHONPATH=.` is required for console entry points, or package the `tools` command modules so installed scripts work without it.
- Acceptance: a new contributor can run install, smoke, local-gate, and diagnostic commands from the documented package root without guessing.

### Phase 1 — Governance/meta-test closure

Close the current governance and meta-test failures before major feature work.

- Add or correct the missing `TEST_DECLARATION` for `tests/contract/test_mapping_apply_rollback.py`.
- Reconcile the package entry registry role expected by `test_meta_package_entry_surfaces`.
- Restore or explicitly register the retained pass2 hardening guide traceability record.
- Reconcile the active package root-layer allowlist with the intended front-door documents.
- Update controlled docs only where the documentation-impact validator proves phrase drift.
- Acceptance: full pytest has zero governance/meta failures, or any remaining failures are explicitly registered as accepted debt with owner, rationale, and review path.

### Phase 2 — Baseline debt registry

Classify lint, format, and type debt instead of mass-fixing it.

- Group ruff findings by module and severity, starting with `F821`, invalid syntax, unused imports, and import-order churn.
- Group mypy findings by subsystem and error category.
- Decide whether format baseline should be applied once or enforced only on touched files.
- Establish a no-new-lint/type-debt policy for touched files.
- Acceptance: a debt registry exists and local gate can distinguish baseline debt from new regressions.

### Phase 3 — Controlled mapping trajectory

Keep mapping work bounded until governance is green.

- Preserve the boundary between shell-local draft edits and runtime-authoritative state.
- Keep dry-run/prepared-only behavior available for operator review.
- Make controller-authorized mapping apply the next technical mapping step only after governance and package-root issues are closed.
- Acceptance: live apply remains impossible unless explicitly authorized through the controller boundary, with dry-run/prepared-only behavior preserved.

### Phase 4 — Device/signal mapping architecture

Clarify the operator workflow without duplicating concepts.

- Device Explorer discovers physical/logical adapter I/O.
- Signal Explorer exposes normalized internal signals and variables.
- Mapping UI binds device I/O to signals with review, preflight, diff, and rollback.
- Keep LabJack, Raspberry Pi, Arduino, Modbus, and other vendor-specific code behind adapter/support-pack/plugin boundaries.
- Acceptance: no duplicated UI concepts, no vendor-specific core leakage, and a clear operator review workflow.

### Phase 5 — Degraded-condition behavior

Prove stale/unavailable state behavior before expanding live authority.

- Simulate devices and signals disappearing, reappearing, and near-simultaneous dropout/reconnect.
- Verify mappings, plots, logic, historian projections, and diagnostics do not corrupt state under degraded conditions.
- Add replay/simulation coverage where possible before requiring real hardware.
- Acceptance: dropped devices/signals become stale or unavailable without corrupting mappings, plots, logic, or historian data.

### Phase 6 — UI validation after headless/core stability

Keep UI dependencies optional while preparing manual validation paths.

- Preserve headless smoke paths and optional UI extras.
- Validate GUI launch in an appropriate display environment.
- Scope UI work to dockable/reconfigurable panels, resettable layouts, persistent settings, trace styling, PiP restore, color-coded status sections, and mapping workflow clarity.
- Acceptance: GUI can launch in a suitable display environment and has a smoke/diagnostic path that does not require live hardware.

## Recommended sprint decision

Begin with Phase 0 and Phase 1 as the next sprint scope. Defer controller-authorized mapping apply and UI expansion until package-root, console-entry, and governance/meta-test failures are closed or explicitly accepted as documented debt.
