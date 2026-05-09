---
document_id: "UDQ-GAP-RPT-001"
title: "Open Implementation Gaps"
revision: "r8"
status: "WIP"
document_class: "gap_report"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-SOP-001"
  - "UDQ-GOV-REG-003"
  - "UDQ-REQ-MAT-001"
  - "UDQ-IMP-PLAN-001"
supersedes:
  - "UDQ-GAP-RPT-001__Open_Implementation_Gaps__r7__WIP.md"
revision_history:
  - "r8 | 2026-03-21 | Reconciled the gap report to the current shell/service save-point baseline and split remaining work from documentation-update debt."
  - "r7 | 2026-03-21 | Reframed the largest remaining gap as execution of Sprint 1 typed model work under the new documentation-impact controls."
---
# Open Implementation Gaps [SEC:UDQ-GAP-RPT-001::0]

## 1. Current largest remaining gaps [SEC:UDQ-GAP-RPT-001::1]

1. The bounded shell/service baseline exists, but strict-tool proof for Ruff and mypy has not yet been demonstrated in the package evidence.
2. Several active registries and generated snapshots still carry scaffold-era package IDs or `SCAFFOLDED` status language and must be regenerated coherently.
3. Physical output actuation, authorization depth, and observed-mismatch proof remain intentionally gated.
4. Remote parity, rules runtime, sequence runtime, and deep adapter/protocol work remain out of scope and unimplemented.
5. The new documentation-debt register must now be used as a normal closure mechanism whenever reviewed stale docs are intentionally deferred.

## 2. Positive closure already achieved [SEC:UDQ-GAP-RPT-001::2]

- typed first-slice model code exists
- shell/service composition exists
- the 15 meaningful contract, scenario, and invariant tests now execute real assertions
- root-layer cleanup and controlled entry-document migration are complete
- documentation-impact procedure exists and now includes explicit debt logging

## 3. Immediate next gap-closing target [SEC:UDQ-GAP-RPT-001::3]

The next bounded sprint should function as a reconciliation and save-point sprint: clean remaining stale registry/snapshot language, freeze the bounded public surface, strengthen proof tooling, and leave the package in a low-ambiguity restart state.
