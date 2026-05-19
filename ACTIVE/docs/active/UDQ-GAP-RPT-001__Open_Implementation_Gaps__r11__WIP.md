
---
document_id: UDQ-GAP-RPT-001
title: Open Implementation Gaps
revision: r14
status: WIP
document_class: gap_report
owner: UniversalDAQ
depends_on:
  - "UDQ-ARCH-NAR-001"
  - "UDQ-ARCH-NAR-002"
  - "UDQ-REQ-MAT-001"
supersedes:
  - "UDQ-GAP-RPT-001__Open_Implementation_Gaps__r11__WIP.md"
revision_history:
  - "r14 | 2026-03-30 | Documentation closeout: reclassified the biggest remaining gaps after device-centered shell consolidation, tag unification, and draft/simulated logic-slice documentation."
  - "r13 | 2026-03-27 | Global documentation reconciliation: reclassified the biggest remaining gaps after bounded cross-device read-side closure and bounded command/arbitration gap hardening."
  - "r12 | 2026-03-26 | Updated the runtime-evidence gap interpretation to reflect new replay reporting, history-tier summaries, and automated acceptance surfaces while keeping long-run historian depth and broader workbench restoration open."
  - "r11 | 2026-03-25 | Docs-only UI refinement pass. Updated the UI-related gaps to reflect that the workspace model, Control workspace, graph semantics, and sequence-convenience posture are now better documented even though implementation remains open."
---
# Open Implementation Gaps [SEC:UDQ-GAP-RPT-001::0]

## 1. Current largest remaining gaps [SEC:UDQ-GAP-RPT-001::1]
1. Controller-backed authoritative mapping readback and later safe apply remain open. The shell can now describe device-centered inspection, tags, and draft state coherently, but applied mutation through the controller seam is still deferred.
2. Authoritative binding availability remains runtime-dependent and is still unavailable in some bounded contexts.
3. True live secondary-axis behavior and broader advanced trace effects remain intentionally deferred even though the trace-style baseline is now better documented and partially wired.
4. Logic Designer has a first executable draft/simulated slice, but runtime-authoritative logic deployment, broader sequencing depth, and generalized orchestration remain deferred.
5. Broader hardware-family generalization and optional proof-tool execution remain environment-dependent or deferred.

## 2. Positive closure already achieved [SEC:UDQ-GAP-RPT-001::2]
- repeatable historian/recovery baseline
- bounded cross-device read-side acquisition closure
- bounded cross-device command/arbitration slice
- degraded and reintroduced device handling as a first-class documented concern on both read and write lanes
- one-command acceptance as the stable operator proof surface

## 3. Interpretation note [SEC:UDQ-GAP-RPT-001::3]
The biggest cross-device gap is no longer “can multiple adapters coexist canonically?” The package has already answered that in bounded form. The biggest remaining gap is now “how do those bounded canonical read/write objects become first-class governed objects inside the control environment and operator surface without broadening the platform prematurely?”

## 4. Human review focus [SEC:UDQ-GAP-RPT-001::4]
A reviewer should confirm that the package now treats read-side closure and first-form write-side closure as achieved bounded sections, while still honestly keeping control-environment richness, broader output breadth, and broader hardware generalization open.

## 5. What is not a gap anymore [SEC:UDQ-GAP-RPT-001::5]
The following should no longer be described as missing in the current package:
- canonical cross-device tag identity,
- simultaneous mixed-source ingest,
- mixed-source replay/fallback proof in bounded form,
- bounded canonical writable tags,
- bounded ownership/arbitration with explicit rejection and degraded handling.
