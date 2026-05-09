---
document_id: UDQ-SCHEMA-POLICY-001
title: Governance Schema Conventions
revision: r0
status: WIP
document_class: schema_policy
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-SPEC-002"
  - "UDQ-GOV-POL-002"
revision_history:
  - "r0 | 2026-03-23 | Registered and normalized for the documentation closeout governance pass."
---
# UDQ-SCHEMA-POLICY-001 — Governance Schema Conventions

## Purpose
Reduce schema drift before machine-readable artifacts become code-facing dependencies.

## Rules
- identifiers remain stable string keys
- list-like values should be stored as arrays whenever practical
- legacy delimiter-packed strings may remain for compatibility, but new structured companion fields should be preferred when code will consume the data
- field names should be semantically consistent across related registries and snapshots
- schema changes should be paired with updated diagnostics or tests

## Immediate application
For next-sprint consumption, first-slice snapshots should prefer structured companion fields such as:
- `primary_source_ids`
- `downstream_spec_ids`
- `intended_module_areas`
- `affected_requirement_ids`

## Non-goal
This policy does not require a full formal schema platform in this package. It does require consistent direction and validation hooks.
