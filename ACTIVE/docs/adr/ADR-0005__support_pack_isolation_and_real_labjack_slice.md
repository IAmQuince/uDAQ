---
document_id: ADR-0005
title: Support-Pack Isolation and the First Real LabJack Slice
revision: r0
status: BASELINE
document_class: architecture_decision_record
owner: UniversalDAQ
depends_on:
  - "UDQ-DEV-SPEC-001"
  - "UDQ-LIFECYCLE-SPEC-001"
revision_history:
  - "r0 | 2026-03-23 | Registered accepted ADR for the documentation closeout governance pass."
---
# ADR-0005 — Support-Pack Isolation and the First Real LabJack Slice

Status: Accepted
Date: 2026-03-23

## Decision
Keep the first real hardware path inside `universaldaq_labjack` and do not allow the universal core to import vendor-specific code.

## Why
The narrow U6 read path is meant to prove value without collapsing the universal model into a LabJack-native core.

## Consequence
Real hardware support is now available in a bounded way, but all vendor-specific behavior stays at the edge.
