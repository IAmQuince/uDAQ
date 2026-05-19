---
document_id: ADR-0006
title: Bounded Safe Expression Evaluation
revision: r0
status: BASELINE
document_class: architecture_decision_record
owner: UniversalDAQ
depends_on:
  - "UDQ-LOG-SPEC-001"
  - "UDQ-LIFECYCLE-SPEC-001"
revision_history:
  - "r0 | 2026-03-23 | Registered accepted ADR for the documentation closeout governance pass."
---
# ADR-0006 — Bounded Safe Expression Evaluation

Status: Accepted
Date: 2026-03-23

## Decision
Retain the AST-whitelist expression evaluator, but add explicit limits for expression length, node budget, evaluation steps, and exponent magnitude.

## Why
The whitelist approach was already correct directionally, but bounded user-authored expressions need deterministic abuse limits.

## Consequence
Expression handling remains reviewable and safe for the bounded shell slice while avoiding open-ended complexity growth.
