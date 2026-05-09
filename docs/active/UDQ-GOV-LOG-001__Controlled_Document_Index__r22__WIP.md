
---
document_id: "UDQ-GOV-LOG-001"
title: "Controlled Document Index"
revision: "r23"
status: "WIP"
document_class: "controlled_index"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-GOV-SPEC-002"
  - "UDQ-GOV-STD-002"
  - "UDQ-GOV-STD-003"
  - "UDQ-GOV-SPEC-003"
  - "UDQ-GOV-SPEC-006"
  - "UDQ-IMP-PLAN-001"
supersedes:
  - "UDQ-GOV-LOG-001__Controlled_Document_Index__r22__WIP.md"
revision_history:
  - "r23 | 2026-03-27 | Updated for the global documentation reconciliation pass after cross-device command/arbitration gap hardening."
  - "r22 | 2026-03-25 | Updated for the docs-only UI refinement pass to surface the refreshed UI document touch set."
---
# Controlled Document Index [SEC:UDQ-GOV-LOG-001::0]

## 1. Purpose [SEC:UDQ-GOV-LOG-001::1]
This index identifies the active controlled UniversalDAQ document set used for package assembly and audit review.

## 2. Active revision rule [SEC:UDQ-GOV-LOG-001::2]
The active working revision for a controlled document is the single revision present under `docs/active/`.

## 3. Current package posture [SEC:UDQ-GOV-LOG-001::3]
The current package line is the bounded documentary baseline after:
- long-run historian/recovery closure,
- cross-device read-side closure,
- bounded cross-device command/arbitration implementation,
- command gap hardening,
- and this global documentation reconciliation pass.

## 4. Current active touch set [SEC:UDQ-GOV-LOG-001::4]
The most directly updated controlled documents for the current package are:
- root README and handbook/release entry surfaces
- `UDQ-DEV-SPEC-001`
- `UDQ-OUT-SPEC-001`
- `UDQ-REQ-MAT-001`
- `UDQ-GAP-RPT-001`
- this controlled document index

## 5. Reviewer note [SEC:UDQ-GOV-LOG-001::5]
The package should now be reviewed as one bounded coherent state description rather than as a sequence of loosely interpreted sprint summaries.
