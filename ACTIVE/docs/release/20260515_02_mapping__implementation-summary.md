# Sprint 1 implementation summary

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Implemented

- Added sandbox mapping state objects and deterministic state hashing.
- Added sandbox apply controller for prepared/dry-run mapping requests.
- Added rollback token and state restoration.
- Added mapping diff report data and Markdown export helper.
- Added GUI Testing menu specification and Qt shell wiring.
- Added no-hardware diagnostic bundle export.
- Added root batch launchers for the app and diagnostics.

## Not implemented

- Live mapping apply.
- Authoritative runtime mutation.
- Physical output writes.
- Hardware-in-loop validation.

## Code surfaces touched

- `src/universaldaq/mapping/`
- `src/universaldaq/testing/`
- `src/universaldaq/ui/visible_shell.py`
- `src/universaldaq/ui/qt_shell.py`
- `tools/dev/run_sprint_diagnostics.py`
- Sprint-specific tests under `tests/`.
