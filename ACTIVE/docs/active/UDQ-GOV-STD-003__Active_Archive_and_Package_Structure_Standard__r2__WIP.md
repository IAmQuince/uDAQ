---
document_id: "UDQ-GOV-STD-003"
title: "Active Archive and Package Structure Standard"
revision: "r2"
status: "WIP"
document_class: "governance_standard"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-IMP-MAP-001"
  - "UDQ-IMP-SPEC-002"
  - "UDQ-GOV-SPEC-006"
supersedes:
  - "UDQ-GOV-STD-003__Active_Archive_and_Package_Structure_Standard__r1__WIP.md"
revision_history:
  - "r2 | 2026-03-21 | Added governed rules for pre-code tests/, tools/, tests/data snapshots, and first-slice src package markers."
  - "r1 | 2026-03-21 | Added required root human-facing guidance documents and control-tower generated reports to the package-structure standard."
---
# Active Archive and Package Structure Standard [SEC:UDQ-GOV-STD-003::0]

## 1. Core rule [SEC:UDQ-GOV-STD-003::1]

Exactly one active revision of each controlled document ID shall live in `docs/active/`. Older revisions shall live in `docs/archive/`.

## 2. Required human-facing root files [SEC:UDQ-GOV-STD-003::2]

The package root shall contain the human entry files defined by `UDQ-GOV-SPEC-006`, including implementation-entry and tests/tools navigation guidance.

## 3. Generated report placement [SEC:UDQ-GOV-STD-003::3]

Generated governance and audit reports shall live under `audit_reports/active/` with older generated report sets preserved under `audit_reports/archive/` where practical.

## 4. Pre-code scaffolding rule [SEC:UDQ-GOV-STD-003::4]

Before broad application code begins, the package shall contain a governed pre-code scaffolding layer composed of:
- executable `tests/` subtrees organized by verification purpose rather than source file
- `tools/` subtrees organized by governance, audit, traceability, diagnostics, packaging, proof, and developer workflow responsibilities
- generated first-slice snapshots under `tests/data/`
- minimal `src/universaldaq/.../__init__.py` package markers and local guardrail `README.md` files for the first allowed module areas

## 5. Output placement rule [SEC:UDQ-GOV-STD-003::5]

The following placement rules are mandatory:
- mutable runtime state belongs under `runtime/`
- proof/evidence artifacts belong under `proof/`
- generated governance and audit summaries belong under `audit_reports/active/`
- executable verification assets belong under `tests/`
- project machinery that is not product runtime belongs under `tools/`
