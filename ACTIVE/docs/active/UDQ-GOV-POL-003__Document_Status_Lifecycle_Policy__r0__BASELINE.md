---
document_id: UDQ-GOV-POL-003
title: Document Status Lifecycle Policy
revision: r0
status: BASELINE
document_class: governance_policy
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-GOV-POL-002"
revision_history:
  - "r0 | 2026-03-23 | Introduced the current document-status lifecycle policy used during documentation closeout."
---
# UDQ-GOV-POL-003 — Document Status Lifecycle Policy

Document ID: UDQ-GOV-POL-003  
Status: BASELINE  
Owner: Core Architecture  
Authority: PRIMARY  
Revision: r0  

## Purpose
Document status labels must communicate whether an asset is provisional, currently authoritative, or retained for history.

## Allowed active statuses
- `DRAFT` — evolving content that is useful but not yet treated as the settled baseline
- `BASELINE` — active content that matches the current bounded implementation or working procedure
- `SUPERSEDED` — historical or replaced content retained for traceability

## Immediate policy for this package line
- release and handbook entry documents should prefer `ACTIVE` or `BASELINE` where they describe implemented behavior
- new policy or ADR assets created for the rebalancing sprint should avoid ambiguous `WIP` labeling when they are being used as current guidance
- older active controlled specs may retain filename-era `WIP` markers until a larger document-baseline cleanup sprint deliberately renames them
