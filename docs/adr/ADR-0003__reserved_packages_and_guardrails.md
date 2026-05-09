---
document_id: ADR-0003
title: Reserved packages and guardrails
revision: r0
status: BASELINE
document_class: architecture_decision_record
owner: UniversalDAQ
depends_on:
  - "UDQ-IMP-MAP-001"
  - "UDQ-GOV-STD-003"
revision_history:
  - "r0 | 2026-03-23 | Registered accepted ADR for the documentation closeout governance pass."
---
# ADR-0003 — Reserved packages and guardrails

## Status
Accepted

## Decision
Deferred subsystems remain present as reserved directories but must contain explicit guardrail files and no active implementation during the next sprint.

## Rationale
The project needs stable package boundaries without encouraging speculative code in out-of-scope areas.

## Consequences
- reserved packages must contain a README guardrail
- meta tests should fail if reserved packages gain active implementation files too early
