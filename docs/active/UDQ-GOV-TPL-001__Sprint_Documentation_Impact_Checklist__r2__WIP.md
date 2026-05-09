---
document_id: UDQ-GOV-TPL-001
title: Sprint Documentation Impact Checklist
revision: r2
status: WIP
document_class: governance_template
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-SOP-001"
  - "UDQ-GOV-REG-003"
  - "UDQ-GOV-TPL-002"
  - "UDQ-GOV-WI-001"
supersedes:
  - "UDQ-GOV-TPL-001__Sprint_Documentation_Impact_Checklist__r1__WIP.md"
revision_history:
  - "r2 | 2026-03-22 | Added the mandatory running documentation review ledger and explicit link to the step-by-step work instruction."
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
- location of the running documentation review ledger maintained with `UDQ-GOV-TPL-002`

## Closeout checks [SEC:UDQ-GOV-TPL-001::2]
- governing spec / ADR updated if needed
- contradiction / duplication / debt registers updated if needed
- running documentation review ledger completed with outcomes for every reviewed asset
- registry and snapshot changes reconciled if needed
- code and package markers updated if needed
- tests and diagnostics updated
- controlled entry documents updated or explicitly reviewed
- release notes / manifest / save-point summary updated
- `python -m tools.governance.validate_document_impact --package-root .`
- `python -m tools.governance.validate_readme_control --package-root .`
- `python -m tools.governance.validate_document_debt --package-root .`
- `python -m tools.dev.run_local_gate --package-root .`
