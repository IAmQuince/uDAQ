---
document_id: UDQ-GOV-REG-001
title: Contradiction and Reconciliation Register
revision: r0
status: WIP
document_class: governance_register
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-002
  - UDQ-GOV-GLO-001
  - UDQ-GOV-RPT-001
revision_history:
  - "r0 | 2026-03-21 | Initial contradiction register for the foundation hardening sprint."
---
# Contradiction and Reconciliation Register {#gov-reg-001.s01}

## 1. Purpose [SEC:UDQ-GOV-REG-001::1]

This register records detected contradictions or material semantic ambiguities, their ruling, and their closure status.

## 2. Closure rule [SEC:UDQ-GOV-REG-001::2]

A register item is considered closed only when the owning semantic source and affected downstream documents have been updated or when the item is explicitly elevated as an open decision that blocks downstream use.

## 3. Current register entries [SEC:UDQ-GOV-REG-001::3]

| Issue ID | Class | Term / Topic Cluster | Source Document(s) | Finding Summary | Canonical Ruling | Resolution Vehicle | Status |
|---|---|---|---|---|---|---|---|
| UDQ-CON-001 | CONTRADICTION | active revision self-reference | UDQ-GOV-LOG-001 r14 | The active set table listed the index itself as r13 even though the file revision was r14. | The controlled index shall identify its own highest active revision truthfully. | UDQ-GOV-LOG-001 r15 | RESOLVED |
| UDQ-CON-002 | CONTRADICTION | stale cross-reference | UDQ-GOV-RPT-001 r2 | The scope section referenced `UDQ-GOV-LOG-001 r6`, which no longer represented the active set. | Package reports shall reference the current active controlled set rather than stale historical set labels. | UDQ-GOV-RPT-001 r3 | RESOLVED |
| UDQ-CON-003 | AMBIGUITY | profile / restore / machine state | UDQ-GOV-GLO-001 r0, UDQ-PROF-SPEC-001 r0, UDQ-ARCH-NAR-001 r3, UDQ-UI-MOD-001 r1 | The corpus separated local continuity from live truth, but the glossary did not yet define profile, autosave, restore, workspace state, and machine state tightly enough to govern all docs. | Restore is local/session/configuration reconstruction and shall not imply authoritative live machine reassertion. | UDQ-GOV-GLO-001 r1, UDQ-GOV-STD-002 r0, UDQ-EXM-SPEC-001 r0 | RESOLVED |
| UDQ-CON-004 | AMBIGUITY | requested / applied / observed state | UDQ-GOV-GLO-001 r0, UDQ-OUT-SPEC-001 r1, UDQ-UI-NAR-001 r1, UDQ-REM-SPEC-001 r1 | The runtime doctrine already distinguished these terms, but the owning glossary definitions were too sparse to prevent future shadow definitions. | Requested, applied, and observed state are separate and glossary-owned, with backend authority over applied and observed publication semantics. | UDQ-GOV-GLO-001 r1, universalDAQ_term_usage_matrix_r1 | RESOLVED |
| UDQ-CON-005 | AMBIGUITY | live / historical / review / live trace | UDQ-UI-SPEC-004 r0, UDQ-HIS-SPEC-001 r1, UDQ-UI-MOD-001 r1, UDQ-UI-NAR-001 r1 | The corpus used these terms consistently in spirit, but the semantic edges between them were not formalized centrally enough. | Live trace is live explainability, historical review is evidence exploration, and review mode is the broader UI posture that may include historical exploration. | UDQ-GOV-GLO-001 r1, UDQ-EXM-SPEC-001 r0 | RESOLVED |
