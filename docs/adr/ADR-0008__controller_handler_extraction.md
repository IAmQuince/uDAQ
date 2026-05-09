---
document_id: ADR-0008
title: Controller Handler Extraction
revision: r0
status: BASELINE
document_class: architecture_decision_record
owner: UniversalDAQ
depends_on:
  - "UDQ-LIFECYCLE-SPEC-001"
  - "UDQ-UI-DEVFLOW-001"
revision_history:
  - "r0 | 2026-03-23 | Registered accepted ADR for the documentation closeout governance pass."
---
# ADR-0008 — Controller Handler Extraction

Status: Accepted
Date: 2026-03-23

## Decision
Keep `ShellController` as the shell-facing façade, but move concentrated lifecycle and binding/variable command groups into focused handler modules.

## Why
The controller had become the major responsibility concentration point in the codebase. A bounded extraction reduces cognitive load without a destabilizing rewrite.

## Consequence
Lifecycle and binding/variable flows are easier to test and review independently, while external controller behavior remains stable.
