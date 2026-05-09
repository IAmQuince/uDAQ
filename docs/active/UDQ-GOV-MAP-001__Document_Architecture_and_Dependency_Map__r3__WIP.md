---
document_id: "UDQ-GOV-MAP-001"
title: "Document Architecture and Dependency Map"
revision: "r3"
status: "WIP"
document_class: "governance_map"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-GOV-STD-003"
  - "UDQ-GOV-SPEC-003"
  - "UDQ-GOV-SPEC-006"
supersedes:
  - "UDQ-GOV-MAP-001__Document_Architecture_and_Dependency_Map__r2__WIP.md"
revision_history:
  - "r3 | 2026-03-21 | Added the control-tower flow from active docs to registries to governance model to execution contract and human-facing summaries."
  - "r2 | 2026-03-21 | Updated for hardening sprint."
---
# Document Architecture and Dependency Map [SEC:UDQ-GOV-MAP-001::0]

## 1. Core architecture flow [SEC:UDQ-GOV-MAP-001::1]

The active package now flows through these layers:

1. controlled source corpus in `docs/active/`
2. machine-readable derivative registries in `registries/active/`
3. global governance model
4. implementation-facing execution contract
5. human-facing status outputs and future implementation attachment points

## 2. High-level dependency rules [SEC:UDQ-GOV-MAP-001::2]

- governance specs depend on the glossary, precedence rules, and requirement matrix
- executive-summary outputs depend on governance registries and readiness posture
- future code shall depend on the execution contract rather than scraping markdown prose

## 3. Human-facing layer [SEC:UDQ-GOV-MAP-001::3]

The root readmes are package navigation artifacts. They are required for package usability but remain subordinate to the active controlled corpus.
