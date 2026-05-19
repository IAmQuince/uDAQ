# Feature inventory — active handoff baseline

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Implemented / embodied in active source baseline

- Device/signal/variable mapping concepts from the uDAQ architecture baseline.
- Authoritative backend/controller readback path inherited from prior sprints.
- Controlled mapping proposal, preflight validation, review summary, and prepared request flow.
- Controller-authorized dry-run commit boundary for mapping apply.
- Non-mutating dry-run results and audit-event records.
- Shell-facing review states for accepted/rejected dry-run workflows.
- Contract tests inherited from `_10` for mapping preflight/review and dry-run commit behavior.

## Documentation/governance features added in this handoff baseline

- Top-level `ACTIVE/` and `HISTORICAL/` lanes.
- Formal active/historical lane governance.
- Handoff manifest and package metadata.
- May stale-identity reconciliation ledger.
- Path-budget/unzip-readiness report.
- Handoff acceptance test plan.

## Explicitly deferred

- Live mapping apply execution.
- Runtime/hardware remapping.
- Hardware-in-loop apply verification.
- Runtime logic deployment and safe-output authority.
- Full sandbox mutation/rollback proof.
