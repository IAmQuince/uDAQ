---
document_id: "UDQ-GOV-SPEC-006"
title: "Executive Summary and Project Status Specification"
revision: "r0"
status: "WIP"
document_class: "governance_spec"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-SPEC-003"
  - "UDQ-GOV-LOG-001"
  - "UDQ-REQ-MAT-001"
supersedes:
revision_history:
  - "r0 | 2026-03-21 | Added the root executive-summary and project-status requirements for human catch-up and handoff."
---
# Executive Summary and Project Status Specification [SEC:UDQ-GOV-SPEC-006::0]

## 1. Purpose [SEC:UDQ-GOV-SPEC-006::1]

This specification defines the required human-facing summary layer for UniversalDAQ package revisions.

## 2. Required root documents [SEC:UDQ-GOV-SPEC-006::2]

The package root shall include:
- `README_START_HERE.md`
- `README_EXEC_SUMMARY.md`
- `README_NEXT_ACTIONS.md`
- `README_HUMAN_PASS.md`
- `README_AUDIT_AND_GOVERNANCE.md`

## 3. Distinct roles [SEC:UDQ-GOV-SPEC-006::3]

These documents shall serve distinct roles:
- `README_START_HERE` — orientation and navigation
- `README_EXEC_SUMMARY` — current project posture
- `README_NEXT_ACTIONS` — exact recommended path forward
- `README_HUMAN_PASS` — review and sign-off guidance
- `README_AUDIT_AND_GOVERNANCE` — how truth flows through the package

## 4. Generated reports [SEC:UDQ-GOV-SPEC-006::4]

The package shall also generate:
- `UDQ_EXECUTIVE_SUMMARY__<timestamp>.md`
- `UDQ_GOVERNANCE_STATUS__<timestamp>.md`

## 5. Minimum content [SEC:UDQ-GOV-SPEC-006::5]

The executive summary layer shall explicitly state:
- package identity and disposition
- implementation posture
- key truths and constraints
- readiness by subsystem or domain
- blockers or deferred decisions
- recommended next sprint focus
- actions that must not be taken yet

## 6. Anti-confusion rule [SEC:UDQ-GOV-SPEC-006::6]

The executive summary shall not be treated as a replacement for controlled technical specifications. It is a catch-up and navigation layer that must remain consistent with the active controlled corpus and machine-readable registries.
