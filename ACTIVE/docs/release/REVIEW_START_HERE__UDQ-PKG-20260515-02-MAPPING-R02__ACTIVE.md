# Review start here — 20260515_02_mapping

**CANONICAL CURRENT REVIEW ENTRY DOCUMENT**

**Controlled release document**  
ID: UDQ-REL-REVIEW-START-20260515-002  
Status: ACTIVE  
Revision: r1  
Owner: Core Architecture  
Authority: PRIMARY  
Source docs: UDQ-ROADMAP-SPEC-001, UDQ-SPRINT-SOP-001, UDQ-LIFECYCLE-SPEC-001, UDQ-EXP-SPEC-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Review purpose

Review this package as Sprint 1: sandbox-only mapping mutation proof. It is not a live hardware control package.

## What to inspect first

1. `README_START_HERE.md`
2. `PACKAGE_MANIFEST.md`
3. `docs/release/EXEC_SUMMARY.md`
4. `docs/release/RELEASE_NOTES.md`
5. `docs/testing/20260515_02_manual-test-checklist.md`
6. `src/universaldaq/mapping/sandbox.py`
7. `src/universaldaq/testing/sprint_mapping.py`
8. `tests/contract/test_mapping_apply_sandbox_boundary.py`
9. `tests/contract/test_mapping_apply_rollback.py`

## Acceptance focus

The key review question is whether sandbox mapping apply can mutate only sandbox state, produce evidence, and rollback without live execution.

## Explicit exclusions

Do not review this package as a live mapping apply, Modbus, output authority, production historian, or hardware-in-loop package; those are future sprints.

## Mandatory classification rule for this review

Use the controlled document header and registry classification as authoritative. Legacy filename suffixes like `__WIP` are not authoritative by themselves. Valid review classifications include ACTIVE, ARCHIVED, RECORD, BASELINE, SUPERSEDED, and DRAFT when the corresponding active registry/header assigns that state.

legacy filename suffixes like `__WIP` are not authoritative by themselves.
