---
document_id: "UDQ-GOV-TPL-001"
title: "Sprint Documentation Impact Checklist"
revision: "r0"
status: "WIP"
document_class: "governance_template"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-SOP-001"
  - "UDQ-GOV-SPEC-004"
  - "UDQ-REQ-MAT-001"
supersedes: []
revision_history:
  - "r0 | 2026-03-21 | Initial checklist template for sprint and pull-request documentation impact control."
---
# Sprint Documentation Impact Checklist [SEC:UDQ-GOV-TPL-001::0]

Use this checklist at sprint open, pull-request preparation, and sprint close.

## 1. Work item identity [SEC:UDQ-GOV-TPL-001::1]
- Work item / branch / package name:
- Change class:
- Governing source(s):

## 2. Impact map [SEC:UDQ-GOV-TPL-001::2]
- Affected modules:
- Affected requirement IDs:
- Affected invariant IDs:
- Affected tests:
- Affected proof outputs:
- Affected controlled docs:
- Affected registries / generated snapshots:
- Reviewed but intentionally unchanged docs:

## 3. Required update sequence [SEC:UDQ-GOV-TPL-001::3]
- [ ] governing spec / ADR updated if needed
- [ ] decision / contradiction / duplication registers updated if needed
- [ ] requirement / invariant / coverage registries updated if needed
- [ ] tests, fixtures, and snapshots updated
- [ ] executive summary, implementation entry, next actions, and audit nav updated
- [ ] release notes and manifest updated

## 4. Validation [SEC:UDQ-GOV-TPL-001::4]
- [ ] `python -m tools.governance.validate_document_impact --package-root .`
- [ ] `python -m tools.dev.run_local_gate --package-root .`
- [ ] additional commands:

## 5. Reconciliation close [SEC:UDQ-GOV-TPL-001::5]
- [ ] changed code paths match changed docs paths
- [ ] requirement / invariant / test links resolve
- [ ] document index reflects the active revisions
- [ ] gap report and next actions reflect the new state
