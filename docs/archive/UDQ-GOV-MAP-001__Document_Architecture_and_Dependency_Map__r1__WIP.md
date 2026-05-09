---
document_id: UDQ-GOV-MAP-001
title: Document Architecture and Dependency Map
revision: r1
status: WIP
document_class: governance-map
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-STD-002
  - UDQ-GOV-SPEC-002
  - UDQ-GOV-GLO-001
revision_history:
  - "r1 | 2026-03-21 | Added semantic precedence context, implementation-transition layer, and the controlled handoff relationship to future code architecture."
  - "r0 | 2026-03-21 | Defines document-layer ordering and dependency intent across the active corpus."
---
# Document Architecture and Dependency Map {#gov-map-001.s01}

## 1. Purpose [SEC:UDQ-GOV-MAP-001::1]

This document defines the major layers of the UniversalDAQ documentation system and the intended dependency direction between them.

## 2. Dependency principle [SEC:UDQ-GOV-MAP-001::2]

Documents shall generally depend downward from governance and architecture into subsystem specifications, then into implementation-transition guidance, then into operational forms and package/report artifacts. Reverse dependency from foundation documents onto templates or reports is not allowed.

## 3. Document layers [SEC:UDQ-GOV-MAP-001::3]

### 3.1 Governance layer [SEC:UDQ-GOV-MAP-001::3.1]
Includes document control, machine-readable scheme, glossary, semantic precedence, controlled index, contradiction/duplication registers, and consistency assessment.

### 3.2 Foundation architecture layer [SEC:UDQ-GOV-MAP-001::3.2]
Includes the system controls narrative, platform controls narrative, requirements traceability matrix, and definition of complete.

### 3.3 UI foundation layer [SEC:UDQ-GOV-MAP-001::3.3]
Includes UI doctrine, functional architecture, and interaction/state model.

### 3.4 Runtime subsystem layer [SEC:UDQ-GOV-MAP-001::3.4]
Includes rules, signals, outputs, Modbus, sequences, historian, remote supervision, alarms, diagnostics, profiles, device abstraction, exports, and authorization.

### 3.5 UI detail layer [SEC:UDQ-GOV-MAP-001::3.5]
Includes shell behavior, workspace/page surfaces, graphing/review/live trace, rules editor roundtrip, visual language, and remote UI surfaces.

### 3.6 Implementation transition layer [SEC:UDQ-GOV-MAP-001::3.6]
Includes the implementation transition plan, proposed code architecture/module boundary map, and canonical worked examples used to anchor later code work.

### 3.7 Proof, audit, and release layer [SEC:UDQ-GOV-MAP-001::3.7]
Includes proof model, package audit spec, scan policy, version control scheme, release package composition, and templates for gap, proof, audit, release, and scan reports.

## 4. Human review order [SEC:UDQ-GOV-MAP-001::4]

A human reconciliation pass should typically move in this order:
1. governance, glossary, and semantic precedence;
2. contradiction and duplication registers;
3. foundation narratives and traceability;
4. subsystem specifications;
5. UI detail documents;
6. implementation-transition documents;
7. proof/audit/release documents;
8. templates and package artifacts.
