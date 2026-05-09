---
document_id: "UDQ-IMP-MAP-001"
title: "Frozen Package Structure and Module Boundary Standard"
revision: "r2"
status: "WIP"
document_class: "implementation_map"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-STD-003"
  - "UDQ-GOV-SPEC-003"
  - "UDQ-GOV-SPEC-004"
supersedes:
  - "UDQ-IMP-MAP-001__Frozen_Package_Structure_and_Module_Boundary_Standard__r1__WIP.md"
revision_history:
  - "r2 | 2026-03-21 | Added governance-control-tower root artifacts and clarified that future code consumes the execution contract rather than active markdown directly."
  - "r1 | 2026-03-21 | Structure-freeze map introduced."
---
# Frozen Package Structure and Module Boundary Standard [SEC:UDQ-IMP-MAP-001::0]

## 1. Current frozen root [SEC:UDQ-IMP-MAP-001::1]

The frozen package root includes:
- active/archive controlled docs
- active/archive registries
- active/archive audit reports
- root human-facing guidance files
- frozen future implementation skeleton directories under `src/`, `tests/`, `proof/`, `runtime/`, and `tools/`

## 2. Key implementation rule [SEC:UDQ-IMP-MAP-001::2]

Future implementation modules shall align to the execution contract and requirement registry. They shall not rely on ad hoc scraping of active markdown to determine runtime behavior.

## 3. First intended module areas [SEC:UDQ-IMP-MAP-001::3]

The first allowed implementation slice is expected to begin in:
- `src/universaldaq/app`
- `src/universaldaq/common`
- `src/universaldaq/signals`
- `src/universaldaq/historian`
- `src/universaldaq/profiles`
- `src/universaldaq/ui`
- `tools/traceability`
