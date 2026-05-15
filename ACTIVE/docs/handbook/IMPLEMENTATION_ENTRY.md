# Implementation entry

**CANONICAL CURRENT ENTRY DOCUMENT**

**Controlled document**  
ID: UDQ-HANDBOOK-IMPLEMENTATION-ENTRY-001  
Status: ACTIVE  
Revision: r21  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-IMP-PLAN-001, UDQ-IMP-GUIDE-001, UDQ-GOV-SOP-001, UDQ-ROADMAP-SPEC-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Current implementation baseline

The active implementation baseline is inherited from the prior handoff baseline, which itself derives from `20260330_10_controller-authorized-mapping-apply-dry-run-commit-boundary`.

## Current source/test roots

- `src/`
- `tests/`
- `tools/`

These paths are relative to `ACTIVE/`.

## Current boundary

- Controller-authorized dry-run mapping apply commit is present.
- Dry-run commit is non-mutating.
- Draft shell edits remain non-authoritative.
- Sandbox mapping mutation remains deferred to Sprint 1.
- Live mapping apply remains deferred.
- Hardware-specific support remains outside core architecture.

## Implementation notes

For future implementation work, start from `ACTIVE/`, not from `HISTORICAL/`. Use `HISTORICAL/` only for lineage, regression comparison, and prior decision context.
