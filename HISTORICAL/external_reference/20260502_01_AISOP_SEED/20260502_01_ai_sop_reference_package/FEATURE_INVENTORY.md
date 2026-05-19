---
document_id: DOC-000-FEATURE-INVENTORY
title: "Feature Inventory"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-000-FEATURE-INVENTORY
normative_status: Normative
source: "Generalized AI-assisted coding SOP source text"
---

# Feature Inventory

## Purpose

This file records the current feature set of the package using stable feature IDs. Future edits should update this file before changing or removing package behavior.

FEAT-001
Name: Generalized AI-assisted coding SOP package
Description: Provides a cleaned, generalized set of AI-assisted coding workflow documents.
Status: Current
Preserve: Yes
Verification: TEST-PKG-002

FEAT-002
Name: Structured markdown documentation library
Description: Splits the source material into topical markdown documents under `docs/`.
Status: Current
Preserve: Yes
Verification: TEST-DOC-003

FEAT-003
Name: Document-control metadata
Description: Adds a machine-readable document-control header to each markdown document.
Status: Current
Preserve: Yes
Verification: TEST-DOC-001

FEAT-004
Name: Machine-referenceable package requirements
Description: Captures package-level requirements using stable `REQ-*` IDs and mirrors them into JSON.
Status: Current
Preserve: Yes
Verification: TEST-DOC-002

FEAT-005
Name: Acceptance test plan
Description: Defines `TEST-*` acceptance items linked to requirement IDs.
Status: Current
Preserve: Yes
Verification: TEST-TEST-001

FEAT-006
Name: Package structure audit
Description: Provides `tools/package_structure_audit.py` to validate required files, metadata, naming, and personal-reference cleanup.
Status: Current
Preserve: Yes
Verification: TEST-AUDIT-001

FEAT-007
Name: Smoke test harness
Description: Provides `tests/smoke_test.py` for a minimal executable package check.
Status: Current
Preserve: Yes
Verification: TEST-SMOKE-001

FEAT-008
Name: Reports folder
Description: Stores audit and smoke-test reports under `reports/`.
Status: Current
Preserve: Yes
Verification: TEST-AUDIT-001, TEST-SMOKE-001

FEAT-009
Name: Example package skeleton
Description: Includes root docs, `docs/`, `tools/`, `tests/`, `reports/`, `requirements/`, `config/`, and `src/` folders to model a future code package.
Status: Current
Preserve: Yes
Verification: TEST-PKG-001
