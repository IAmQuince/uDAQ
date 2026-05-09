---
document_id: UDQ-GOV-SOP-001
title: Controlled Document Update and Impact Process
revision: r3
status: WIP
document_class: governance_sop
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-GOV-SPEC-002"
  - "UDQ-GOV-SPEC-003"
  - "UDQ-GOV-POL-002"
  - "UDQ-GOV-REG-003"
supersedes:
  - "UDQ-GOV-SOP-001__Controlled_Document_Update_and_Impact_Process__r2__WIP.md"
revision_history:
  - "r3 | 2026-03-21 | Added the mandatory documentation-update debt register workflow so stale docs that are not updated immediately are explicitly logged rather than silently carried forward."
  - "r2 | 2026-03-21 | Formalized sprint-open impact mapping, mandatory update order, and handbook/release/review document reconciliation."
---
# Controlled Document Update and Impact Process [SEC:UDQ-GOV-SOP-001::0]

## 1. Purpose [SEC:UDQ-GOV-SOP-001::1]

This SOP defines how documentation impact is identified, updated, deferred, validated, and closed during a bounded sprint or package revision.

## 2. Core rule [SEC:UDQ-GOV-SOP-001::2]

Material documentation drift is not allowed to remain invisible.

When a contributor finds a materially stale controlled asset and chooses not to update it within the same bounded change, that asset shall be entered in `UDQ-GOV-REG-003` before the package closes.

## 3. Required sprint-open impact map [SEC:UDQ-GOV-SOP-001::3]

Every bounded change shall begin with an impact map covering:
- affected modules
- affected requirement IDs
- affected invariant IDs
- affected controlled docs
- affected controlled entry documents / READMEs
- affected registries and generated snapshots
- affected tests and proof outputs
- reviewed but intentionally unchanged docs
- reviewed but intentionally unchanged entry documents
- reviewed but intentionally deferred docs that must be added to the documentation debt register

Use `UDQ-GOV-TPL-001` as the working template.

## 4. Update order [SEC:UDQ-GOV-SOP-001::4]

For semantic or architectural changes, update in this order:
1. governing spec, glossary, or ADR
2. contradiction / duplication / debt registers as needed
3. requirement / invariant / coverage / consistency registries if affected
4. snapshots, fixtures, and proof expectations
5. code and package markers
6. tests and diagnostics
7. handbook / release / review documents and controlled READMEs
8. release notes, manifest, and save-point summary

## 5. Deferred-update rule [SEC:UDQ-GOV-SOP-001::5]

A document may be intentionally left unchanged when immediate update is not necessary for the bounded change, but only if one of the following is true:
- the document was reviewed and found still correct,
- the document is derived and still accurately summarizes its sources,
- or the document is materially stale and has a debt entry in `UDQ-GOV-REG-003` with owner, target, and status.

## 6. Sprint close [SEC:UDQ-GOV-SOP-001::6]

Before a package closes, contributors shall:
- reconcile code paths against updated docs,
- confirm controlled entry documents were updated or intentionally left unchanged,
- close or log every known documentation discrepancy,
- run the documentation-impact validator,
- run the README-control validator,
- run the documentation-debt validator,
- and update release-facing summary documents.
