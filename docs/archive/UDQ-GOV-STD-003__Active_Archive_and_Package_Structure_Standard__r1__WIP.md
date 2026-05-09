---
document_id: "UDQ-GOV-STD-003"
title: "Active Archive and Package Structure Standard"
revision: "r1"
status: "WIP"
document_class: "governance_standard"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-IMP-MAP-001"
  - "UDQ-GOV-SPEC-006"
supersedes:
  - "UDQ-GOV-STD-003__Active_Archive_and_Package_Structure_Standard__r0__WIP.md"
revision_history:
  - "r1 | 2026-03-21 | Added required root human-facing guidance documents and control-tower generated reports to the package-structure standard."
  - "r0 | 2026-03-21 | Active/archive split introduced."
---
# Active Archive and Package Structure Standard [SEC:UDQ-GOV-STD-003::0]

## 1. Core rule [SEC:UDQ-GOV-STD-003::1]

Exactly one active revision of each controlled document ID shall live in `docs/active/`. Older revisions shall live in `docs/archive/`.

## 2. Required human-facing root files [SEC:UDQ-GOV-STD-003::2]

The package root shall contain the human entry files defined by `UDQ-GOV-SPEC-006`.

## 3. Generated report placement [SEC:UDQ-GOV-STD-003::3]

Generated governance and audit reports shall live under `audit_reports/active/` with older generated report sets preserved under `audit_reports/archive/` where practical.
