---
document_id: "UDQ-GOV-SOP-001"
title: "Controlled Document Update and Impact Process"
revision: "r2"
status: "WIP"
document_class: "governance_sop"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-SPEC-003"
  - "UDQ-GOV-SPEC-004"
  - "UDQ-GOV-SPEC-006"
  - "UDQ-REQ-MAT-001"
  - "UDQ-IMP-PLAN-001"
  - "UDQ-GOV-POL-002"
supersedes:
  - "UDQ-GOV-SOP-001__Controlled_Document_Update_and_Impact_Process__r1__WIP.md"
revision_history:
  - "r2 | 2026-03-21 | Added mandatory sprint documentation impact mapping, PR checklist expectations, README-control integration, reconciliation closeout, and validation hooks."
  - "r1 | 2026-03-21 | Added governance-model, execution-contract, coverage-matrix, and executive-summary update steps."
  - "r0 | 2026-03-21 | Controlled update process introduced."
---
# Controlled Document Update and Impact Process [SEC:UDQ-GOV-SOP-001::0]

## 1. Purpose [SEC:UDQ-GOV-SOP-001::1]

This SOP defines the minimum update procedure for any sprint or bounded implementation change that affects governed semantics, machine-readable registries, tests, operational READMEs, package summaries, or release composition.

## 2. Required planning artifact [SEC:UDQ-GOV-SOP-001::2]

Before work starts, the sprint or pull request shall produce a **documentation impact map** that identifies for each work item:
- affected modules
- affected requirement IDs
- affected invariant IDs
- affected controlled documents
- affected controlled READMEs
- affected registries and generated snapshots
- affected tests and proof outputs
- documents and READMEs intentionally reviewed but unchanged

## 3. Change classes [SEC:UDQ-GOV-SOP-001::3]

Each work item shall be classified as one or more of:
1. **semantic / governance change**
2. **implementation change**
3. **verification change**
4. **packaging / process change**

The change class determines which documents and registries must be updated.

## 4. Mandatory update order [SEC:UDQ-GOV-SOP-001::4]

For any semantic, architectural, or boundary change, the update order shall be:
1. governing specification, glossary, or ADR
2. contradiction / duplication / decision registers as needed
3. requirement matrix and requirement registry
4. execution contract, invariant registry, and coverage matrix if affected
5. tests, fixtures, worked-example snapshots, and proof expectations
6. controlled READMEs, implementation-entry briefing, executive summary, next actions, and audit navigation
7. diagnostics, audit outputs, and release notes / manifest

## 5. Pull-request and package checklist [SEC:UDQ-GOV-SOP-001::5]

Every implementation pull request or review package shall explicitly state:
- what changed
- governing source(s)
- affected requirement IDs
- affected invariant IDs
- controlled docs updated
- controlled READMEs updated
- registries regenerated
- documents and READMEs intentionally left unchanged after review
- validation commands run locally

## 6. Reconciliation closeout [SEC:UDQ-GOV-SOP-001::6]

A sprint is not complete until a reconciliation pass confirms that:
- changed code paths are reflected in changed docs paths
- requirement, invariant, and test links still resolve
- the document index and gap report reflect the new state
- release-facing summaries match the actual bounded change
- controlled README revisions and registry entries still agree

## 7. Validation hooks [SEC:UDQ-GOV-SOP-001::7]

- `python -m tools.governance.validate_document_impact --package-root .` validates the required sprint-documentation-control assets.
- `python -m tools.governance.validate_readme_control --package-root .` validates controlled README registry coverage and required control strips.
