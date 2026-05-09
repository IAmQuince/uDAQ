---
document_id: UDQ-GOV-MAP-001
title: Document Architecture and Dependency Map
revision: r0
status: WIP
document_class: governance-map
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-SPEC-002
  - UDQ-GOV-GLO-001
revision_history:
  - revision: r0
    date: 2026-03-21
    summary: Defines document-layer ordering and dependency intent across the active corpus.
---
# Document Architecture and Dependency Map {#gov-map-001.s01}

## 1. Purpose [SEC:UDQ-GOV-MAP-001::1]

This document defines the major layers of the UniversalDAQ documentation system and the intended dependency direction between them.

## 2. Dependency Principle [SEC:UDQ-GOV-MAP-001::2]

Documents shall generally depend downward from governance and architecture into subsystem specifications, then into operational forms and package/report artifacts. Reverse dependency from foundation documents onto templates or reports is not allowed.

## 3. Document Layers [SEC:UDQ-GOV-MAP-001::3]

### 3.1 Governance Layer [SEC:UDQ-GOV-MAP-001::3.1]
Includes document control, machine-readable scheme, glossary, controlled index, and consistency assessment.

### 3.2 Foundation Architecture Layer [SEC:UDQ-GOV-MAP-001::3.2]
Includes the system controls narrative, platform controls narrative, requirements traceability matrix, and definition of complete.

### 3.3 UI Foundation Layer [SEC:UDQ-GOV-MAP-001::3.3]
Includes UI doctrine, functional architecture, and interaction/state model.

### 3.4 Runtime Subsystem Layer [SEC:UDQ-GOV-MAP-001::3.4]
Includes rules, signals, outputs, Modbus, sequences, historian, remote supervision, alarms, diagnostics, profiles, device abstraction, exports, and authorization.

### 3.5 UI Detail Layer [SEC:UDQ-GOV-MAP-001::3.5]
Includes shell behavior, workspace/page surfaces, graphing/review/live trace, rules editor roundtrip, visual language, and remote UI surfaces.

### 3.6 Proof, Audit, and Release Layer [SEC:UDQ-GOV-MAP-001::3.6]
Includes proof model, package audit spec, scan policy, version control scheme, release package composition, and templates for gap, proof, audit, release, and scan reports.

## 4. Typical Forward Flow [SEC:UDQ-GOV-MAP-001::4]

1. Governance establishes document rules and identifiers.
2. Foundation architecture defines platform obligations.
3. Subsystem and UI detail documents specialize those obligations.
4. Proof/audit/release documents define how completion and package integrity are judged.
5. Templates operationalize those judgments into repeatable working artifacts.

## 5. Review Order for Human Passes [SEC:UDQ-GOV-MAP-001::5]

A human reconciliation pass should typically move in this order:
1. Governance and glossary.
2. Foundation narratives and traceability.
3. Subsystem specifications.
4. UI detail documents.
5. Proof/audit/release documents.
6. Templates and package artifacts.
