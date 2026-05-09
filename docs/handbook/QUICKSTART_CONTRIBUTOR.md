# UniversalDAQ — Contributor Quickstart

**Controlled document**  
ID: UDQ-README-QUICKSTART-001  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-README-ROOT-001, UDQ-README-START-001, ADR-0007  

## Use this document when
- you are making a bounded bug fix,
- you are touching the LabJack U6 proof slice,
- or you need the shortest path to a valid local review package.

## Minimum workflow
1. Read `README.md` and `docs/handbook/START_HERE.md`.
2. Confirm the change is in scope for the current sprint line.
3. Make the code change and the directly related test change together.
4. Update the active sprint or release summary.
5. Run `python -m tools.dev.run_local_gate --package-root .`.
6. If your change touches the LabJack slice, also run `python -m tools.dev.run_labjack_u6_smoke --package-root .`.

## For a real-device check later
Run:
- `python -m tools.dev.run_labjack_u6_smoke --package-root . --real-hardware`

This expects a locally available LabJack U6 driver and a connected device.
The one-command acceptance runner now also emits a bounded real-hardware bridge result; if no U6 is present it must report SKIP explicitly rather than pretending the hardware lane passed.

## What you do not need to do for every bounded fix
- touch every active governance document,
- expand registries or tooling unless the change truly requires it,
- or reopen deferred roadmap areas just because the package contains placeholders for them.


## U6 hardware evidence
When a change touches the bounded real U6 line, prefer `tools\dev\run_u6_field_test_harness.bat` so the review can happen from a small evidence bundle rather than console copy/paste.
