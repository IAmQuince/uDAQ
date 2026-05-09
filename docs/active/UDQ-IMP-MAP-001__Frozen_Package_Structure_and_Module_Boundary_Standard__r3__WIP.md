---
document_id: "UDQ-IMP-MAP-001"
title: "Frozen Package Structure and Module Boundary Standard"
revision: "r3"
status: "WIP"
document_class: "implementation_map"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-STD-003"
  - "UDQ-GOV-SPEC-003"
  - "UDQ-GOV-SPEC-004"
  - "UDQ-IMP-SPEC-002"
supersedes:
  - "UDQ-IMP-MAP-001__Frozen_Package_Structure_and_Module_Boundary_Standard__r2__WIP.md"
revision_history:
  - "r3 | 2026-03-21 | Froze the initial tests/ and tools/ subtrees and aligned first-slice src package markers with execution-contract module areas."
  - "r2 | 2026-03-21 | Added governance-control-tower root artifacts and clarified that future code consumes the execution contract rather than active markdown directly."
---
# Frozen Package Structure and Module Boundary Standard [SEC:UDQ-IMP-MAP-001::0]

## 1. Current frozen root [SEC:UDQ-IMP-MAP-001::1]

The frozen package root includes:
- active/archive controlled docs
- active/archive registries
- active/archive audit reports
- root human-facing guidance files
- frozen pre-code scaffolding directories under `src/`, `tests/`, `proof/`, `runtime/`, and `tools/`

## 2. Key implementation rule [SEC:UDQ-IMP-MAP-001::2]

Future implementation modules shall align to the execution contract, requirement registry, invariant registry, and first-slice snapshots. They shall not rely on ad hoc scraping of active markdown to determine runtime behavior.

## 3. First allowed module areas [SEC:UDQ-IMP-MAP-001::3]

The first allowed implementation slice begins in:
- `src/universaldaq/app`
- `src/universaldaq/common`
- `src/universaldaq/signals`
- `src/universaldaq/outputs`
- `src/universaldaq/events`
- `src/universaldaq/historian`
- `src/universaldaq/profiles`
- `src/universaldaq/ui`
- `tools/traceability`
- `tools/governance`

## 4. Frozen verification tree [SEC:UDQ-IMP-MAP-001::4]

The initial governed verification tree shall include:
- `tests/meta`
- `tests/smoke`
- `tests/contract`
- `tests/scenario`
- `tests/invariants`
- `tests/regression`
- `tests/integration`
- `tests/fixtures`
- `tests/data`
- `tests/baselines`

## 5. Frozen project-machinery tree [SEC:UDQ-IMP-MAP-001::5]

The initial governed project-machinery tree shall include:
- `tools/governance`
- `tools/traceability`
- `tools/audit`
- `tools/diagnostics`
- `tools/package_build`
- `tools/proof`
- `tools/dev`

## 6. Boundary caution [SEC:UDQ-IMP-MAP-001::6]

The first code sprint may create model and declaration scaffolding in the allowed module areas. It shall not cross into physical output actuation, remote command actuation, broad rules execution, sequence runtime behavior, or deep protocol/device implementation.
