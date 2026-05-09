---
document_id: UDQ-GOV-TPL-002
title: Documentation Review and Outcome Ledger Template
revision: r0
status: WIP
document_class: governance_template
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-SOP-001"
  - "UDQ-GOV-WI-001"
  - "UDQ-GOV-REG-003"
revision_history:
  - "r0 | 2026-03-22 | Introduced a required ledger template so every reviewed controlled asset has an explicit outcome during a bounded change."
---
# Documentation Review and Outcome Ledger Template [SEC:UDQ-GOV-TPL-002::0]

Use one row for every controlled asset reviewed during a bounded change.

| asset_path | asset_id | class | review_scope | outcome | action_taken | debt_id | owner | notes |
|---|---|---|---|---|---|---|---|---|
| docs/active/example.md | UDQ-EXAMPLE-001 | active_doc | semantic change | UPDATED | revised to reflect new boundary |  | Core Architecture |  |
| docs/handbook/example.md | UDQ-README-EXAMPLE-001 | controlled_readme | release summary review | REVIEWED_OK | no change needed |  | Core Architecture | still matches source docs |
| registries/active/example.json | registry | generated artifact | package closeout | DEFERRED_STALE | not regenerated in this bounded change | UDQ-DOCDEBT-999 | Core Architecture | regenerate in next registry pass |

## Outcome vocabulary [SEC:UDQ-GOV-TPL-002::1]
- `UPDATED`
- `REVIEWED_OK`
- `DEFERRED_STALE`
- `SUPERSEDED`
- `GENERATED_NOCHANGE`
- `OUT_OF_SCOPE`
