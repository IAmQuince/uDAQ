---
document_id: UDQ-GOV-SOP-002
title: Controlled Document Completeness and Recovery Process
revision: r0
status: WIP
document_class: governance_sop
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-GOV-SOP-001"
  - "UDQ-GOV-REG-003"
  - "UDQ-GOV-WI-001"
supersedes: []
revision_history:
  - "r0 | 2026-03-24 | WIP | Created after the truncation-recovery run to formalize pre-zip completeness gating, donor-aware recovery, and post-zip shipped-artifact verification."
---
# Controlled Document Completeness and Recovery Process [SEC:UDQ-GOV-SOP-002::0]

## 1. Purpose [SEC:UDQ-GOV-SOP-002::1]
This SOP defines the mandatory controls used to prevent accidental truncation, stub replacement, or incomplete packaging of controlled documentation.

## 2. Core rule [SEC:UDQ-GOV-SOP-002::2]
No package may be released when a controlled document body is incomplete, suspiciously collapsed, or not verified against its canonical source.

## 3. Trigger conditions [SEC:UDQ-GOV-SOP-002::3]
This SOP shall be used whenever any of the following occur:
- a controlled document appears markedly shorter than its prior known revision,
- a controlled document loses major section depth without an explicit revision rationale,
- a packaged artifact appears cut off at the end,
- a cleanup or regeneration step touched active controlled documents,
- or a reviewer reports that a controlled or entry document appears to have been replaced by a stub.

## 4. Required records [SEC:UDQ-GOV-SOP-002::4]
Every recovery or verification run shall produce:
- a document recovery matrix,
- a document completeness proof,
- a donor/source selection note for each restored asset,
- and a shipped-artifact verification result produced after the zip is created.

## 5. Completeness gate [SEC:UDQ-GOV-SOP-002::5]
Before a package is accepted, all controlled active documents shall pass:
1. structural section presence checks appropriate to document class,
2. end-of-file integrity checks,
3. suspicious shrinkage checks against prior revisions when available,
4. and graph / registry / path-resolution checks from the ordinary governance audit.

A validator failure is release-blocking unless a documented exception is explicitly approved and logged.

## 6. Recovery order [SEC:UDQ-GOV-SOP-002::6]
When a document is suspected damaged, recover in this order:
1. freeze the suspect package as evidence,
2. identify the canonical donor source,
3. restore full body content before metadata normalization,
4. reconcile registry/cross-reference consequences,
5. run completeness validation,
6. create the release zip,
7. reopen the zip and verify the shipped artifact itself.

## 7. Donor selection rule [SEC:UDQ-GOV-SOP-002::7]
Preferred donor order is:
1. same document ID from the immediately prior coherent package,
2. archived prior revision inside the package tree,
3. generated source asset or authoritative template,
4. explicit manual reconstruction only when no canonical donor exists.

The chosen donor and the reason for choosing it shall be logged in the recovery matrix.

## 8. Anti-truncation implementation controls [SEC:UDQ-GOV-SOP-002::8]
The package shall retain a dedicated completeness validator and a meta test that exercise the validator. Cleanup or packaging steps that write into active controlled docs shall be treated as high-risk operations and verified after execution.

## 9. Post-zip shipped-artifact rule [SEC:UDQ-GOV-SOP-002::9]
Validation of the working tree alone is insufficient. The created zip must be reopened and checked so the shipped artifact is proven to contain the same complete controlled-document bodies that were verified in the workspace.

## 10. Closeout [SEC:UDQ-GOV-SOP-002::10]
A truncation-recovery run closes only when:
- restored assets are listed,
- completeness proof is present,
- the shipped zip has been rechecked,
- and future validator/audit hooks were updated so the same class of failure is harder to repeat.

## 11. Baseline snapshot and shrinkage guard [SEC:UDQ-GOV-SOP-002::11]
When a package already exists and an in-place follow-on sprint touches active code or controlled docs, a baseline file snapshot shall be captured before edits and compared after edits. The comparison shall flag missing tracked files, zero-byte tracked files, missing terminal newlines, and suspicious shrinkage before packaging.
