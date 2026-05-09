---
document_id: UDQ-GOV-MAP-001
title: Document Architecture and Dependency Map
revision: r2
status: WIP
document_class: governance_map
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-GOV-STD-002"
  - "UDQ-GOV-STD-003"
  - "UDQ-IMP-MAP-001"
supersedes:
  - "UDQ-GOV-MAP-001__Document_Architecture_and_Dependency_Map__r1__WIP.md"
revision_history:
  - "r2 | 2026-03-21 | Updated the governance map for active/archive separation and frozen package structure."
  - "r1 | 2026-03-21 | Added foundation-hardening governance and implementation-transition documents to the dependency architecture map."
---
# Document Architecture and Dependency Map [SEC:UDQ-GOV-MAP-001::0]

## 1. Purpose [SEC:UDQ-GOV-MAP-001::1]

This document summarizes how the active UniversalDAQ controlled corpus is organized after the corpus-closure and structure-freeze sprint.

## 2. Governance stack [SEC:UDQ-GOV-MAP-001::2]

The active corpus should be read in the following order of precedence:

1. governance standards and glossary  
   (`UDQ-GOV-STD-001`, `UDQ-GOV-STD-002`, `UDQ-GOV-STD-003`, `UDQ-GOV-GLO-001`)
2. governance registers, reports, and process docs  
   (`UDQ-GOV-REG-001`, `UDQ-GOV-REG-002`, `UDQ-GOV-RPT-001`, `UDQ-GOV-RPT-002`, `UDQ-GOV-SOP-001`)
3. architecture narratives and subsystem specifications
4. UI architecture/state/detail specifications
5. requirements, quality, release, and audit documents
6. templates and archived historical revisions

## 3. Structure-freeze placement model [SEC:UDQ-GOV-MAP-001::3]

- `docs/active/` is the active controlled corpus.
- `docs/archive/` is historical controlled context.
- `registries/active/` mirrors the active corpus in machine-readable form.
- `audit_reports/active/` holds the current package audit evidence.
- `src/`, `tests/`, `proof/`, `runtime/`, and `tools/` are frozen implementation-entry structure.

## 4. High-risk semantic dependency chains [SEC:UDQ-GOV-MAP-001::4]

- glossary → outputs / profiles / UI state / historian / graphing
- security → outputs / remote / UI enablement behavior
- outputs → graphing / historian / rules / sequences / remote
- profiles + UI state → startup / restore / review continuity
- events + historian → evidence chain / export / graph overlays

## 5. Human review focus [SEC:UDQ-GOV-MAP-001::5]

A human pass should challenge whether any active downstream spec attempts to redefine a glossary-owned term or a higher-precedence doctrine term, especially around command truth, restore boundaries, and live-versus-historical posture.
