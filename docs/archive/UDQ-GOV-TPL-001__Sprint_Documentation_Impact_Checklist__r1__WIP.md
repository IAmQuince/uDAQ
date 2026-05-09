---
document_id: UDQ-GOV-TPL-001
title: Sprint Documentation Impact Checklist
revision: r1
status: WIP
document_class: governance_template
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-SOP-001"
  - "UDQ-GOV-REG-003"
supersedes:
  - "UDQ-GOV-TPL-001__Sprint_Documentation_Impact_Checklist__r0__WIP.md"
revision_history:
  - "r1 | 2026-03-21 | Added explicit review/defer logging and documentation-debt register handling."
---
# Sprint Documentation Impact Checklist [SEC:UDQ-GOV-TPL-001::0]

## Impact map fields [SEC:UDQ-GOV-TPL-001::1]
- affected modules
- affected requirement IDs
- affected invariant IDs
- affected tests / proof outputs
- affected controlled docs
- affected controlled entry documents / READMEs
- affected registries / generated snapshots
- reviewed but intentionally unchanged docs
- reviewed but intentionally unchanged entry documents
- reviewed but intentionally deferred docs to be logged in `UDQ-GOV-REG-003`

## Closeout checks [SEC:UDQ-GOV-TPL-001::2]
- governing spec / ADR updated if needed
- contradiction / duplication / debt registers updated if needed
- registry and snapshot changes reconciled if needed
- code and package markers updated if needed
- tests and diagnostics updated
- controlled entry documents updated or explicitly reviewed
- release notes / manifest / save-point summary updated
- `python -m tools.governance.validate_document_impact --package-root .`
- `python -m tools.governance.validate_readme_control --package-root .`
- `python -m tools.governance.validate_document_debt --package-root .`
- `python -m tools.dev.run_local_gate --package-root .`
