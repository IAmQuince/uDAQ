---
document_id: UDQ-IMP-GUIDE-001
title: Python Typing and Modeling Policy
revision: r0
status: WIP
document_class: implementation_guide
owner: UniversalDAQ
depends_on:
  - "UDQ-IMP-PLAN-001"
  - "UDQ-REQ-MAT-001"
revision_history:
  - "r0 | 2026-03-23 | Registered and normalized for the documentation closeout governance pass."
---
# UDQ-IMP-GUIDE-001 — Python Typing and Modeling Policy

## Purpose
Freeze the typing and modeling rules for the first typed-domain-model slice and the immediate next strengthening sprint.

## Runtime baseline
- minimum runtime: Python 3.11
- prefer 3.11-native typing syntax for implementation code
- use `typing_extensions` only when a clearly justified backport is needed

## Modeling rules
- semantic identifiers use `NewType`
- governed state vocabularies use enums
- domain/runtime records use frozen, slotted dataclasses by default
- JSON-like transport/config/test payloads use `TypedDict`
- subsystem boundaries use `Protocol`
- avoid casual `Any` in `common`, `signals`, `outputs`, `events`, `profiles`, `historian`, `ui`, and `app`

## Dataclass defaults
Prefer `@dataclass(frozen=True, slots=True, kw_only=True)` for durable domain models. Use mutable dataclasses only for explicit builders, internal drafts, or accumulators.

## Current implemented enum domains
The bounded slice now implements enums for graph modes, signal quality, command decisions, authorization state, restore origin, evidence kind, and alarm lifecycle state.

## Checker policy
- blocking checker: mypy
- formatter/linter: Ruff
- `strict = true` is not the sole policy; explicit options in `pyproject.toml` are authoritative

## Boundary rule
Accept wide input types at the edges, normalize early, and store narrow governed types internally.
