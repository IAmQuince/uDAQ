---
document_id: UDQ-GOV-SPEC-002
title: Machine Readable Document and Cross Reference Scheme
revision: r4
status: WIP
document_class: governance_spec
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-AUD-SPEC-001
  - UDQ-AUD-SPEC-002
supersedes:
  - UDQ-GOV-SPEC-002__Machine_Readable_Document_and_Cross_Reference_Scheme__r2__WIP.md
---
# UDQ-GOV-SPEC-002 Machine Readable Document and Cross Reference Scheme

## 1. Purpose [SEC:UDQ-GOV-SPEC-002::1]
This specification defines the machine-readable structure used to identify UniversalDAQ documents, sections, requirements, dependencies, and cross-references.

## 2. Core Objects [SEC:UDQ-GOV-SPEC-002::2]
The scheme shall govern controlled documents, sections, requirements, glossary/ontology terms, dependency edges, cross-reference edges, and package/report companion artifacts.

## 3. Minimum Document Metadata [SEC:UDQ-GOV-SPEC-002::3]
Controlled documents shall expose machine-readable metadata sufficient to identify document ID, title, revision, status, class, owner, dependencies, and supersession where applicable.

## 4. Stable Section Anchors [SEC:UDQ-GOV-SPEC-002::4]
Normative sections shall carry stable section anchors sufficient for machine linking and review traceability.

## 5. Cross-Reference Rules [SEC:UDQ-GOV-SPEC-002::5]
Cross-references shall prefer document ID over title-only mention, section anchor over vague section naming where applicable, and registered requirement IDs for requirement traceability.

## 6. Allowed-Pattern Governance Link [SEC:UDQ-GOV-SPEC-002::6]
Machine-readable audit treatment shall distinguish between document class, rule-scoped allowed patterns, and true findings. This scheme shall not support hidden broad exception lists as a primary mechanism for audit suppression.

## 7. Registry Artifacts [SEC:UDQ-GOV-SPEC-002::7]
The controlled corpus shall maintain machine-readable registries sufficient to represent documents, requirements, cross-reference/dependency edges, and consistency findings as needed.

## 8. Revision History [SEC:UDQ-GOV-SPEC-002::8]
- r4: Document-scoped section anchors completed for the active revision and class-based scan allowances clarified.
- r3: Clarified allowed-pattern governance link and disallowed hidden broad exception treatment in the machine-readable scheme.
- r2: Prior stabilized issue.
