---
document_id: UDQ-GOV-SOP-001
title: Controlled Document Update and Impact Process
revision: r0
status: WIP
document_class: governance_process
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-STD-002
  - UDQ-GOV-REG-001
  - UDQ-GOV-REG-002
revision_history:
  - "r0 | 2026-03-21 | Initial issue defining controlled update order and impact propagation."
---
# Controlled Document Update and Impact Process {#gov-sop-001.s01}

## 1. Purpose [SEC:UDQ-GOV-SOP-001::1]

This process defines how governed documents are changed without reintroducing hidden contradiction, silent duplication, or broken downstream traceability.

## 2. Trigger conditions [SEC:UDQ-GOV-SOP-001::2]

This process shall be used whenever a change affects:

- a canonical term meaning,
- authority or ownership semantics,
- state or quality meaning,
- UI meaning that could mislead a future implementation,
- proof expectations,
- package structure or intended code/module boundaries.

## 3. Required update order [SEC:UDQ-GOV-SOP-001::3]

1. update the owning glossary term or higher-precedence governance source,
2. update the contradiction register if ambiguity or conflict is involved,
3. update the duplication register if repeated normative text is introduced or resolved,
4. update affected subsystem or UI specifications,
5. update the term-usage matrix and any impacted machine-readable registries,
6. update the requirements traceability matrix if requirement meaning or coverage changed,
7. rerun the package-root audit,
8. record the change in the package notes or next release note artifact.

## 4. Prohibited shortcuts [SEC:UDQ-GOV-SOP-001::4]

The following shortcuts are not allowed:

- changing downstream prose first and hoping governance catches up later,
- silently redefining a glossary-owned term in a subsystem spec,
- deleting repeated text without checking whether it is the only local operational statement,
- merging two terms because they feel similar,
- changing file structure doctrine without updating the module-boundary map.

## 5. Human pass focus [SEC:UDQ-GOV-SOP-001::5]

A manual review should specifically ask:

- Did the change create a new shadow definition?
- Did the change make any older example misleading?
- Did the change alter the intended ownership of a future code module?
- Did the change require a contradiction or duplication entry that was not added?
