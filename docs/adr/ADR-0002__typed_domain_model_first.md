---
document_id: ADR-0002
title: Typed domain model first
revision: r0
status: BASELINE
document_class: architecture_decision_record
owner: UniversalDAQ
depends_on:
  - "UDQ-IMP-GUIDE-001"
  - "UDQ-REQ-MAT-001"
revision_history:
  - "r0 | 2026-03-23 | Registered accepted ADR for the documentation closeout governance pass."
---
# ADR-0002 — Typed domain model first

## Status
Accepted

## Decision
The next sprint will implement typed, pure model code before adapter, remote, or widget-heavy work.

## Rationale
The first implementation slice is primarily about semantics: authority, requested/applied/observed separation, graph modes, restore semantics, and alarm lifecycles. Those are best established as typed domain models first.

## Consequences
- prioritize IDs, enums, dataclasses, protocols, and TypedDict transport shapes
- replace skipped contract/scenario/invariant tests with model-backed assertions as code lands
- avoid speculative device or network behavior in the next sprint
