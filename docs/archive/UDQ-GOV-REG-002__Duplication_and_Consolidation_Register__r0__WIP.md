---
document_id: UDQ-GOV-REG-002
title: Duplication and Consolidation Register
revision: r0
status: WIP
document_class: governance_register
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-002
  - UDQ-GOV-RPT-001
revision_history:
  - "r0 | 2026-03-21 | Initial duplication register for the foundation hardening sprint."
---
# Duplication and Consolidation Register {#gov-reg-002.s01}

## 1. Purpose [SEC:UDQ-GOV-REG-002::1]

This register records meaningful duplication discovered during the hardening sprint and classifies whether it is acceptable, requires consolidation, or creates semantic risk.

## 2. Review rule [SEC:UDQ-GOV-REG-002::2]

Repeated text or repeated headings are not automatically defects. Duplication becomes governed only when it is classified and assigned a disposition.

## 3. Current register entries [SEC:UDQ-GOV-REG-002::3]

| Issue ID | Duplication Class | Source Document(s) | Duplicate Object | Disposition | Resolution Vehicle | Status |
|---|---|---|---|---|---|---|
| UDQ-DUP-001 | GOVERNED_BOILERPLATE | UDQ-AUD-TPL-001, UDQ-GAP-TPL-001, UDQ-PROOF-TPL-001 | Common template skeleton headings and field group structure | Accepted as a controlled template family because the duplication is structural rather than competing semantic truth. | Register only | ACCEPTED_INTENTIONAL |
| UDQ-DUP-002 | INTENTIONAL_REFERENCE_DUPLICATION | UDQ-ARCH-NAR-001, UDQ-ARCH-NAR-002 | Safe-state precedence language | Kept in both architecture narratives because one states system doctrine and the other states backend/platform authority doctrine. | Governed by glossary and semantic precedence standard | ACCEPTED_INTENTIONAL |
| UDQ-DUP-003 | SHADOW_DEFINITION | UDQ-PROF-SPEC-001, UDQ-ARCH-NAR-001, UDQ-UI-MOD-001 | Restore and local continuity prose | Reduced by moving owning meaning into the glossary and leaving subsystem docs to operationalize rather than redefine. | UDQ-GOV-GLO-001 r1 and UDQ-EXM-SPEC-001 r0 | RESOLVED |
| UDQ-DUP-004 | INTENTIONAL_REFERENCE_DUPLICATION | UDQ-UI-NAR-001, UDQ-UI-ARCH-001 | Signals → rules → actions → live trace chain | Retained because doctrine and architecture both need the chain, but the owning meaning of live trace is now glossary-controlled. | Governed by glossary and term-usage matrix | ACCEPTED_INTENTIONAL |
