# Next Actions

**Controlled document**  
ID: UDQ-HANDBOOK-NEXT-001  
Status: ACTIVE  
Revision: r23  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-GOV-REG-003, UDQ-GOV-LOG-001

**CANONICAL CURRENT NEXT-ACTIONS ENTRY — PACKAGE `UDQ-PKG-20260330-CONTROLLED-MAPPING-APPLY-PREFLIGHT-AND-REVIEW-PATH-R01`**

## Package identity
- Package ID: `UDQ-PKG-20260330-CONTROLLED-MAPPING-APPLY-PREFLIGHT-AND-REVIEW-PATH-R01`

## Best next sprint
`20260330_10_controller-authorized-mapping-apply-dry-run-commit-boundary`

## Why
The system can now build and review non-executing mapping apply requests. The next safe move is to add a controller-authorized commit boundary that still begins in dry-run/non-hardware mode and rejects stale readback.

## Sequence note
- Authoritative readback is implemented.
- Draft edits remain intentionally non-authoritative.
- Preflight/review/prepared-request generation is implemented.
- Live hardware apply, runtime logic deployment, and hardware-in-loop verification remain deferred until a controller-authorized commit model is separately reviewed and tested.

## Reconciliation continuity note
The phase 3 shell semantics and documentation reconciliation baseline remain valid; the next sprint should extend controlled apply through an explicit commit boundary rather than bypassing review.
