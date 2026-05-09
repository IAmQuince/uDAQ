---
document_id: UDQ-GOV-POL-002
title: README Control and Classification Policy
revision: r0
status: WIP
document_class: governance_policy
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-GOV-SPEC-002"
revision_history:
  - "r0 | 2026-03-23 | Registered and normalized for the documentation closeout governance pass."
---
# UDQ-GOV-POL-002 — README Control and Classification Policy

## Purpose
This policy brings the root README plus operational handbook/release/review entry documents under lightweight document control without renaming them away from normal repository conventions.

## Classes
- **Primary controlled README** — authoritative for repository entry, implementation entry, audit usage, or tool navigation.
- **Derived controlled README** — summarizes authoritative controlled sources and must name those sources.
- **Uncontrolled README** — temporary or convenience only and excluded from governance claims.

## Required control block
Every controlled README shall include a visible control strip near the top with:
- document ID
- status
- revision
- owner
- authority level
- source document IDs

## Registry
Controlled READMEs shall also be listed in `registries/active/universalDAQ_readme_registry_r0.*`.

## Validation
`python -m tools.governance.validate_readme_control --package-root .` shall validate the presence of control strips and registry coverage for controlled READMEs.


## Root-layer policy
Only the canonical root `README.md` shall remain at the package root. Other operational briefings shall live under `docs/handbook/`, `docs/release/`, or `docs/review/` and stay listed in `registries/active/universalDAQ_readme_registry_r0.*`.
