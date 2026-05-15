# Start here — UniversalDAQ Sprint 1 mapping package

**CANONICAL CURRENT ENTRY DOCUMENT**

**Controlled handoff document**  
ID: UDQ-HANDOFF-START-20260515-002  
Status: ACTIVE  
Revision: r1  
Owner: Core Architecture  
Authority: PRIMARY  
Source docs: UDQ-ROADMAP-SPEC-001, UDQ-SPRINT-SOP-001, UDQ-LIFECYCLE-SPEC-001, UDQ-EXP-SPEC-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## What this package is

This package implements Sprint 1 for UniversalDAQ: a sandbox-only mapping mutation proof. It adds a safe mapping sandbox state, prepared-request apply into sandbox, before/after diff, rollback token, automated diagnostic bundle export, and GUI-visible `Testing` menu actions.

The package still does not implement live mapping apply, physical output authority, Modbus, Logic Designer runtime deployment, or production historian behavior. No hardware is required for the Sprint 1 tests.

## Read in this order

1. `PACKAGE_MANIFEST.md`
2. `docs/release/REVIEW_START_HERE__UDQ-PKG-20260515-02-MAPPING-R02__ACTIVE.md`
3. `docs/release/EXEC_SUMMARY.md`
4. `docs/release/RELEASE_NOTES.md`
5. `docs/testing/20260515_02_manual-test-checklist.md`
6. `docs/handbook/NEXT_ACTIONS.md`
7. `KNOWN_LIMITATIONS.md`

## How to test

From `ACTIVE/`, run `RUN_DIAGNOSTICS.bat` for an automated no-hardware diagnostic bundle. If optional UI dependencies are installed, run `RUN_UDAQ.bat` and use the `Testing` menu.

## Current implementation boundary

Sandbox apply mutates only `MappingSandboxStateStore`. It does not mutate authoritative live runtime state, does not call adapters, does not write outputs, and does not grant live mapping authority.
