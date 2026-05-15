---
document_id: DOC-005
title: "Product Requirements"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-005
normative_status: Normative
source: "Generalized AI-assisted coding SOP source text"
---

# Product Requirements

## Scope

This document is the authoritative machine-referenceable requirement list for this example package.

The long instructional guides in `docs/` are informative reference material unless a requirement in this file explicitly references them. This keeps the example package small while still illustrating how requirements should be captured, traced, tested, and audited.

## Requirement Status Values

- Proposed
- Accepted
- Implemented
- Deferred
- Rejected

## Machine-Referenceable Requirements

REQ-PKG-001
Title: Package naming match
Requirement: The zip filename and internal top-level folder name shall match.
Rationale: Matching names make package intake, auditing, and handoff less ambiguous.
Acceptance test: Open the zip and verify the top-level folder name equals the zip basename.
Priority: Must
Status: Implemented
Verification: TEST-PKG-001

REQ-PKG-002
Title: Start-here documentation
Requirement: The package shall include `README_START_HERE.md` at the root.
Rationale: A reviewer or AI agent needs a deterministic first file to read.
Acceptance test: Confirm the file exists and explains package purpose, usage, and audit commands.
Priority: Must
Status: Implemented
Verification: TEST-PKG-002

REQ-DOC-001
Title: Document control metadata
Requirement: Every markdown document shall include a machine-readable document-control header with document ID, title, version, revision, status, last-updated date, package ID, and normative status.
Rationale: The package itself should demonstrate the documentation discipline it recommends.
Acceptance test: Run `python tools/package_structure_audit.py` and verify all markdown files pass the metadata check.
Priority: Must
Status: Implemented
Verification: TEST-DOC-001

REQ-DOC-002
Title: Machine-referenceable requirements
Requirement: Every normative package requirement shall have a stable ID using the `REQ-*` pattern.
Rationale: Requirements must be traceable across acceptance tests, feature inventory, workplans, and audit reports.
Acceptance test: Confirm this document contains no unnumbered normative requirements and that each `REQ-*` has a linked verification item.
Priority: Must
Status: Implemented
Verification: TEST-DOC-002

REQ-DOC-003
Title: Documentation index
Requirement: The package shall include a documentation index listing the major documents and their intended use.
Rationale: Reviewers should be able to navigate the package without hidden chat context.
Acceptance test: Confirm `docs/000_DOCUMENTATION_INDEX.md` exists and lists the package documents.
Priority: Must
Status: Implemented
Verification: TEST-DOC-003

REQ-FEAT-001
Title: Feature inventory
Requirement: The package shall include `FEATURE_INVENTORY.md` with stable `FEAT-*` IDs.
Rationale: Feature preservation depends on knowing what the package currently contains.
Acceptance test: Confirm each listed feature has an ID, description, status, and verification method.
Priority: Must
Status: Implemented
Verification: TEST-FEAT-001

REQ-TEST-001
Title: Acceptance test plan
Requirement: The package shall include `ACCEPTANCE_TEST_PLAN.md` with stable `TEST-*` IDs mapped to requirements.
Rationale: A requirement without a test is not enforceable.
Acceptance test: Confirm every Must requirement in this file has at least one mapped `TEST-*` item.
Priority: Must
Status: Implemented
Verification: TEST-TEST-001

REQ-AUDIT-001
Title: Structure audit tool
Requirement: The package shall include a runnable structure audit tool under `tools/`.
Rationale: The package should be self-checking and should generate copy/pasteable reports.
Acceptance test: Run `python tools/package_structure_audit.py` and confirm the report is written to `reports/package_structure_audit_report.txt`.
Priority: Must
Status: Implemented
Verification: TEST-AUDIT-001

REQ-SMOKE-001
Title: Smoke test
Requirement: The package shall include a runnable smoke test under `tests/`.
Rationale: The package should demonstrate the minimum test harness expected of future code packages.
Acceptance test: Run `python tests/smoke_test.py` and confirm the report is written to `reports/smoke_test_report.txt`.
Priority: Should
Status: Implemented
Verification: TEST-SMOKE-001

REQ-GEN-001
Title: Generalized wording
Requirement: The deliverable package shall not contain direct personal-name references from the source draft.
Rationale: The package is intended as a reusable consumer-facing seed, not a personal working note.
Acceptance test: Run the audit tool and confirm the personal-reference scan passes.
Priority: Must
Status: Implemented
Verification: TEST-GEN-001

REQ-LIMIT-001
Title: Known limitations
Requirement: The package shall include known limitations and make clear that it is an example seed, not a complete production application.
Rationale: The package should not overclaim completeness.
Acceptance test: Confirm `KNOWN_LIMITATIONS.md` exists and includes first-pass limitations.
Priority: Should
Status: Implemented
Verification: TEST-LIMIT-001

## Requirement Traceability Summary

The machine-readable requirement catalog is also stored at:

`requirements/requirements_catalog.json`

That JSON file is derived from the requirement list above and is intended as a simple example of machine-readable requirement indexing.
