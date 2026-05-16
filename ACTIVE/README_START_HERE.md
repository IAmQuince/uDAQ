# Start here — UniversalDAQ Sprint 2 runtime-state package

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

This package closes Sprint 2 for UniversalDAQ: authoritative runtime-state integration. It preserves the Sprint 1 sandbox-only mapping mutation proof and adds the runtime-state truth spine, compatibility API exports, contract/invariant tests, and runtime-state diagnostic snapshot tooling.

The package still does not implement live mapping apply, physical output authority, Modbus, Logic Designer runtime deployment, or production historian behavior. No hardware is required for the Sprint 2 tests.

## Read in this order

1. `PACKAGE_MANIFEST.md`
2. `docs/release/REVIEW_START_HERE__UDQ-PKG-20260515-02-MAPPING-R02__ACTIVE.md`
3. `docs/release/EXEC_SUMMARY.md`
4. `docs/release/RELEASE_NOTES.md`
5. `docs/testing/20260515_02_manual-test-checklist.md`
6. `docs/architecture/20260515_03_authoritative_runtime_state.md`
7. `docs/handbook/RUNTIME_STATE_DIAGNOSTICS.md`
8. `docs/handbook/NEXT_ACTIONS.md`
9. `KNOWN_LIMITATIONS.md`

## How to test

From `ACTIVE/`, run `RUN_DIAGNOSTICS.bat` for an automated no-hardware diagnostic bundle. If optional UI dependencies are installed, run `RUN_UDAQ.bat` and use the `Testing` menu.

## Current implementation boundary

`RuntimeStateSnapshot` is the authoritative inspectable runtime-state spine. Sandbox apply mutates only `MappingSandboxStateStore`; sandbox projections remain requested/review state and do not mutate authoritative live runtime state, call adapters, write outputs, or grant live mapping authority.
