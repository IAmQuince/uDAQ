# Workplan — 20260515_02_mapping

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Objective

Implement Sprint 1: sandbox-only mapping mutation proof with apply, diff, rollback, GUI-accessible testing entry points, manual test checklist, and diagnostic bundle export.

## In scope

- `MappingSandboxState` and deterministic state hash.
- Prepared request apply into sandbox only.
- Rollback token and state restoration.
- Mapping diff report in JSON/Markdown-friendly form.
- `Testing` menu actions in the visible shell specification and Qt shell wiring.
- `RUN_UDAQ.bat` and `RUN_DIAGNOSTICS.bat`.
- Sprint-specific automated and manual tests.

## Out of scope

- Live mapping apply.
- Hardware output writes.
- Modbus implementation.
- Production historian.
- Runtime logic deployment.
- Broad UI redesign.

## Closeout expectation

The package is complete when changed-area tests, inherited mapping dry-run tests, and package governance checks pass, and when a user can create a no-hardware diagnostic bundle from the batch file or GUI Testing menu.
