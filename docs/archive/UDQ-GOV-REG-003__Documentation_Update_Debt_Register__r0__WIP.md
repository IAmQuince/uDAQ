---
document_id: UDQ-GOV-REG-003
title: Documentation Update Debt Register
revision: r0
status: WIP
document_class: governance_register
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-SOP-001"
  - "UDQ-GOV-REG-001"
  - "UDQ-GOV-RPT-001"
  - "UDQ-GAP-RPT-001"
revision_history:
  - "r0 | 2026-03-21 | Introduced a running register for documents and registries that were reviewed, found stale or partially stale, and intentionally deferred rather than silently left behind."
---
# Documentation Update Debt Register [SEC:UDQ-GOV-REG-003::0]

## 1. Purpose [SEC:UDQ-GOV-REG-003::1]

This register records documentation and registry assets that were reviewed, found to require update, and either:
- corrected in the current sprint,
- intentionally deferred with an owner and target sprint, or
- kept under observation because the cost of immediate update exceeded the bounded sprint scope.

The point is to stop stale language from surviving only as tribal knowledge.

## 2. Required use [SEC:UDQ-GOV-REG-003::2]

If a contributor notices a materially stale controlled document, controlled entry document, registry, snapshot, or package marker and does **not** update it in the same bounded change, the contributor shall add an entry here before the sprint/package closes.

## 3. Current entries [SEC:UDQ-GOV-REG-003::3]

| debt_id | asset | class | finding | disposition | owner | target | status |
|---|---|---|---|---|---|---|---|
| UDQ-DOCDEBT-001 | docs/active/UDQ-GAP-RPT-001__Open_Implementation_Gaps__r7__WIP.md | active_doc | Gap report still stated typed model work had not started and that 15 behavior tests were placeholders. | Corrected in r8 during the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-002 | docs/active/UDQ-IMP-PLAN-001__Implementation_Transition_and_Handoff_Plan__r5__WIP.md | active_doc | Plan still described the next step as the typed-domain-model sprint rather than the post-shell save-point baseline. | Corrected in r6 during the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-003 | tests/README.md | controlled_readme | Test tree README still said contract, scenario, and invariant behavior tests remained scaffolded. | Corrected in the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-004 | src/universaldaq/__init__.py | package_marker | Package marker still identified the repo as only the Sprint 1 typed-domain-model baseline. | Corrected in the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-005 | src/universaldaq/*/README.md reserved package guardrails | controlled_readme | Several reserved-package READMEs still referenced the "next typed-domain-model sprint" instead of a general later-slice boundary. | Corrected in the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-006 | tests/data/first_slice_requirement_pack.json; tests/data/first_slice_invariant_registry.json; tests/data/first_slice_execution_contract.json | snapshot | First-slice snapshots still carried the old sprint1-typed-model package ID and scaffold-era status language. | Package ID corrected now; detailed field-state reconciliation deferred to the next snapshot regeneration pass. | Core Architecture | Next snapshot regeneration sprint | OPEN |
| UDQ-DOCDEBT-007 | registries/active/universalDAQ_requirement_registry_r9.* | registry | Requirement registry still uses scaffold_status = SCAFFOLDED for entries whose bounded first-slice assertions now execute. | Deferred because the registry should be regenerated coherently rather than edited piecemeal. | Core Architecture | Next registry regeneration sprint | OPEN |
| UDQ-DOCDEBT-008 | registries/active/universalDAQ_execution_contract_r2.* | registry | Execution-contract registry still carries scaffold-era status language in several fields. | Deferred to a coherent regeneration pass tied to the next release manifest and baseline audit. | Core Architecture | Next registry regeneration sprint | OPEN |
| UDQ-DOCDEBT-009 | registries/active/universalDAQ_consistency_findings_r9.json | registry | Consistency findings file still carries an older package identity and needs regeneration. | Deferred to the next consistency sweep/regeneration pass. | Core Architecture | Next consistency sweep | OPEN |

| UDQ-DOCDEBT-010 | registries/active/universalDAQ_document_registry_r20.* | registry | Document registry still points to superseded active revision paths for SOP, plan, and gap report, and does not yet register the new debt register or save-point summary. | Deferred to the next registry regeneration pass because the index should be rebuilt coherently. | Core Architecture | Next registry regeneration sprint | OPEN |
| UDQ-DOCDEBT-011 | registries/active/universalDAQ_readme_registry_r0.* | registry | README registry was not yet refreshed to include the new save-point summary entry in both JSON and CSV forms. | Deferred to the next registry regeneration pass. | Core Architecture | Next registry regeneration sprint | OPEN |

## 4. Closure rule [SEC:UDQ-GOV-REG-003::4]

A debt entry closes only when the affected asset is updated or explicitly superseded and the closeout is reflected here with the disposition changed to CLOSED.
