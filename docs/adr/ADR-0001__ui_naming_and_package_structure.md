---
document_id: ADR-0001
title: UI naming and package structure
revision: r0
status: BASELINE
document_class: architecture_decision_record
owner: UniversalDAQ
depends_on:
  - "UDQ-UI-ARCH-001"
  - "UDQ-UI-MOD-001"
revision_history:
  - "r0 | 2026-03-23 | Registered accepted ADR for the documentation closeout governance pass."
---
# ADR-0001 — UI naming and package structure

## Status
Accepted

## Decision
Use `src/universaldaq/ui` for the implementation-facing user-interface package. Keep `app` as bootstrap/orchestration and keep runtime truth in domain packages such as `signals`, `outputs`, `events`, `profiles`, and `historian`.

## Rationale
`frontend` is a useful conceptual word in architecture narratives, but it is not the cleanest package name for a native desktop application. `ui` is shorter, clearer, and less web-specific.

## Consequences
- path references move from `src/universaldaq/frontend` to `src/universaldaq/ui`
- conceptual documentation may still discuss frontend/backend authority where that language is useful
- generic `backend/` shall not become a catch-all implementation bucket
