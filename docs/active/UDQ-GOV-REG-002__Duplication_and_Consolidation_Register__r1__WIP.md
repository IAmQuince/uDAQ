---
document_id: UDQ-GOV-REG-002
title: Duplication and Consolidation Register
revision: r1
status: WIP
document_class: governance_register
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-002"
  - "UDQ-GOV-STD-003"
  - "UDQ-GOV-RPT-001"
  - "UDQ-GOV-RPT-002"
supersedes:
  - "UDQ-GOV-REG-002__Duplication_and_Consolidation_Register__r0__WIP.md"
revision_history:
  - "r1 | 2026-03-21 | Expanded the duplication register during subsystem reconciliation and structure freeze."
  - "r0 | 2026-03-21 | Initial duplication register for the foundation hardening sprint."
---
# Duplication and Consolidation Register [SEC:UDQ-GOV-REG-002::0]

## 1. Purpose [SEC:UDQ-GOV-REG-002::1]

This register records meaningful duplication discovered during the hardening and structure-freeze sprints and classifies whether it is acceptable, requires consolidation, or creates semantic risk.

## 2. Review rule [SEC:UDQ-GOV-REG-002::2]

Repeated text or repeated headings are not automatically defects. Duplication becomes governed only when it is classified and assigned a disposition.

## 3. Current register entries [SEC:UDQ-GOV-REG-002::3]

| issue_id | duplication_class | source_docs | duplicate_object | disposition | resolution_vehicle | status |
|---|---|---|---|---|---|---|
| UDQ-DUP-001 | GOVERNED_BOILERPLATE | UDQ-AUD-TPL-001; UDQ-GAP-TPL-001; UDQ-PROOF-TPL-001 | common template skeleton headings and field groups | Accepted as a controlled template family; duplication is structural rather than competing semantic truth. | Register only | ACCEPTED_INTENTIONAL |
| UDQ-DUP-002 | INTENTIONAL_REFERENCE_DUPLICATION | UDQ-ARCH-NAR-001; UDQ-ARCH-NAR-002 | safe-state doctrine and backend-authority language | Retained because one narrative states whole-system doctrine and the other states platform/backend doctrine. | Governed by glossary and semantic precedence rules | ACCEPTED_INTENTIONAL |
| UDQ-DUP-003 | SHADOW_DEFINITION | UDQ-PROF-SPEC-001 r0; UDQ-UI-MOD-001 r1; UDQ-ARCH-NAR-001 r3 | restore / continuity / machine-state wording | Reduced by moving owning meaning to the glossary and adding explicit anti-conflation language in subsystem docs. | UDQ-PROF-SPEC-001 r1; UDQ-UI-MOD-001 r2 | RESOLVED |
| UDQ-DUP-004 | INTENTIONAL_REFERENCE_DUPLICATION | UDQ-UI-NAR-001; UDQ-UI-ARCH-001; UDQ-UI-MOD-001 | graph-dominant workflow and explainability chain references | Retained as doctrine plus architecture plus interaction-model reinforcement; meanings remain glossary-owned. | Governed by term matrix and worked examples | ACCEPTED_INTENTIONAL |
| UDQ-DUP-005 | SHADOW_DEFINITION | UDQ-HIS-SPEC-001 r1; UDQ-UI-SPEC-004 r0; UDQ-UI-MOD-001 r1 | live / historical / review / live-trace language | Reduced by clarifying term boundaries and letting the graph spec operationalize rather than redefine them. | UDQ-HIS-SPEC-001 r2; UDQ-UI-SPEC-004 r1; UDQ-EXM-SPEC-001 r1 | RESOLVED |
| UDQ-DUP-006 | SHADOW_DEFINITION | UDQ-REM-SPEC-001 r1; UDQ-SEC-SPEC-001 r0; UDQ-OUT-SPEC-001 r1 | authorization and command-acceptance wording | Reduced by assigning backend authorization doctrine to security/output layers and constraining remote docs to capability and attribution behavior. | UDQ-REM-SPEC-001 r2; UDQ-SEC-SPEC-001 r1; UDQ-OUT-SPEC-001 r2 | RESOLVED |
| UDQ-DUP-007 | INTENTIONAL_REFERENCE_DUPLICATION | UDQ-EVT-SPEC-001; UDQ-HIS-SPEC-001 | alarm/event evidence linkage | Retained because event lifecycle and historian evidence must both reference the relationship, but neither may redefine the other's primary object model. | Governed by contradiction register and worked examples | ACCEPTED_INTENTIONAL |
| UDQ-DUP-008 | INTENTIONAL_REFERENCE_DUPLICATION | UDQ-GOV-STD-003; UDQ-IMP-MAP-001 | frozen package root structure | Retained because the governance standard owns placement rules while the implementation map owns module boundary explanation. | Governed by package structure standard | ACCEPTED_INTENTIONAL |
