---
document_id: UDQ-UI-SPEC-005
title: Remote UI Surface Specification
revision: r1
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-REM-SPEC-001
  - UDQ-SEC-SPEC-001
  - UDQ-UI-SPEC-001
  - UDQ-UI-SPEC-002
  - UDQ-UI-SPEC-006
supersedes:
  - UDQ-UI-SPEC-005__Remote_UI_Surface_Specification__r0__WIP.md
revision_history:
  - revision: r1
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Aligned remote surfaces with the Run/Control/Review/System workspace model and clarified that any remote Control functions are policy-bounded and never imply local parity.
  - revision: r0
    date: 2026-03-21
    summary: Defines remote observer and remote supervisor UI surfaces and their limitations.
---
# Remote UI Surface Specification [SEC:UDQ-UI-SPEC-005::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-005::1]

This document defines the concrete UI surface expectations for remote observer and remote supervisor operation.

## 2. Remote Classes [SEC:UDQ-UI-SPEC-005::2]

Remote UI surfaces shall distinguish at least:
- observer-only
- supervisor
- restricted command-capable
- policy-bounded authoring or review access where explicitly allowed

## 3. Required Remote Truth [SEC:UDQ-UI-SPEC-005::3]

Remote surfaces shall make latency, degraded connectivity, read-only limitations, and current authorization boundaries explicit.

## 4. Remote Workspace Alignment [SEC:UDQ-UI-SPEC-005::4]

Remote surfaces may expose bounded subsets of:
- Run
- Review
- System
- selected Control functions where policy allows

No remote surface shall imply that all local Control or System features are available remotely.

## 5. Observer Surface [SEC:UDQ-UI-SPEC-005::5]

The observer surface shall prioritize current values, trends, health, events, and historical review without presenting local-only control affordances as if they were available remotely.

## 6. Supervisor Surface [SEC:UDQ-UI-SPEC-005::6]

The supervisor surface may allow governed acknowledgments, selected supervisory actions, or selected setpoint changes while preserving attribution and backend enforcement.

## 7. Remote Control-Authoring Limits [SEC:UDQ-UI-SPEC-005::7]

If remote Control workspace access is permitted, it shall be explicit about:
- whether authoring is view-only
- whether validation may be run
- whether simulation may be run
- whether apply/deploy is allowed
- what confirmation and attribution rules govern those actions

## 8. Local-Parity Rule [SEC:UDQ-UI-SPEC-005::8]

The remote UI shall not imply local parity when remote capability is intentionally narrower.

## 9. Remote Attribution [SEC:UDQ-UI-SPEC-005::9]

Actions issued from remote surfaces shall be visibly attributable as remote-origin actions in both remote and local review surfaces.

## 10. Human Review Focus [SEC:UDQ-UI-SPEC-005::10]

A reviewer should quickly confirm that remote surfaces now align with the new workspace model and still preserve non-parity, attribution, and policy-bounded capability.
