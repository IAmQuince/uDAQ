---
document_id: DOC-000-ACCEPTANCE-TEST-PLAN
title: "Acceptance Test Plan"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-000-ACCEPTANCE-TEST-PLAN
normative_status: Normative
source: "Generalized AI-assisted coding SOP source text"
---

# Acceptance Test Plan

## Purpose

This document maps package requirements to testable acceptance items. It is intentionally small so the package remains a lightweight reference example.

TEST-PKG-001
Linked requirement: REQ-PKG-001
Type: Automated/manual
Command: `python tools/package_structure_audit.py`
Expected result: Zip/internal package naming rule is documented and package structure is valid.
Status: Implemented

TEST-PKG-002
Linked requirement: REQ-PKG-002
Type: Automated
Command: `python tools/package_structure_audit.py`
Expected result: `README_START_HERE.md` exists and is non-empty.
Status: Implemented

TEST-DOC-001
Linked requirement: REQ-DOC-001
Type: Automated
Command: `python tools/package_structure_audit.py`
Expected result: Every markdown file includes required document-control metadata.
Status: Implemented

TEST-DOC-002
Linked requirement: REQ-DOC-002
Type: Automated/manual
Command: `python tests/smoke_test.py`
Expected result: Requirement IDs are present, unique enough for this package, and mirrored into `requirements/requirements_catalog.json`.
Status: Implemented

TEST-DOC-003
Linked requirement: REQ-DOC-003
Type: Automated
Command: `python tools/package_structure_audit.py`
Expected result: `docs/000_DOCUMENTATION_INDEX.md` exists and is non-empty.
Status: Implemented

TEST-FEAT-001
Linked requirement: REQ-FEAT-001
Type: Automated/manual
Command: `python tests/smoke_test.py`
Expected result: `FEATURE_INVENTORY.md` exists and contains `FEAT-*` entries.
Status: Implemented

TEST-TEST-001
Linked requirement: REQ-TEST-001
Type: Automated/manual
Command: `python tests/smoke_test.py`
Expected result: `ACCEPTANCE_TEST_PLAN.md` exists and contains `TEST-*` entries linked to `REQ-*` IDs.
Status: Implemented

TEST-AUDIT-001
Linked requirement: REQ-AUDIT-001
Type: Automated
Command: `python tools/package_structure_audit.py`
Expected result: Audit completes and writes `reports/package_structure_audit_report.txt`.
Status: Implemented

TEST-SMOKE-001
Linked requirement: REQ-SMOKE-001
Type: Automated
Command: `python tests/smoke_test.py`
Expected result: Smoke test completes and writes `reports/smoke_test_report.txt`.
Status: Implemented

TEST-GEN-001
Linked requirement: REQ-GEN-001
Type: Automated
Command: `python tools/package_structure_audit.py`
Expected result: Personal-reference scan passes.
Status: Implemented

TEST-LIMIT-001
Linked requirement: REQ-LIMIT-001
Type: Manual/automated
Command: `python tools/package_structure_audit.py`
Expected result: `KNOWN_LIMITATIONS.md` exists and is non-empty.
Status: Implemented
