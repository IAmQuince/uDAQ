# Manual test checklist — 20260515_02_mapping

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Scope

This checklist verifies the Sprint 1 user-facing testing entry points and sandbox-only mapping apply behavior. No hardware is required and no live output writes are expected.

## Launch test

1. Extract `20260515_02_mapping-r2.zip` to `C:\Users\iaq16\Documents\Code\uDAQ` or another short path.
2. Open `20260515_02_mapping-r2\ACTIVE`.
3. Double-click `RUN_UDAQ.bat`.
4. Confirm the app opens in user-demo or sandbox/demo posture.
5. Confirm no message claims live mapping apply or output authority is enabled.

Expected result: the visible shell opens when optional UI dependencies are installed. If the UI dependencies are missing, the batch file should print a clear dependency message rather than failing silently.

## Testing menu visibility

1. In the app, confirm the top menu bar contains `Testing`.
2. Open `Testing`.
3. Confirm these actions exist:
   - `Run Smoke Test`
   - `Run Mapping Sandbox Demo`
   - `Run Apply/Rollback Test`
   - `Run Diff Report Test`
   - `Run Visible Shell Wiring Audit`
   - `Export Diagnostic Bundle`
   - `Open Manual Test Checklist`
   - `Open Latest Report Folder`

Expected result: all actions are visible from the GUI menu.

## Automated GUI tests

Run the following from the `Testing` menu:

1. `Run Smoke Test`
2. `Run Mapping Sandbox Demo`
3. `Run Apply/Rollback Test`
4. `Run Diff Report Test`
5. `Run Visible Shell Wiring Audit`
6. `Export Diagnostic Bundle`

Expected result: each action reports pass/fail and writes an artifact under `ACTIVE\audit_reports\testing` or `ACTIVE\diagnostics`.

## Batch diagnostic test

1. Close the app if desired.
2. Double-click `RUN_DIAGNOSTICS.bat`.
3. Wait for the printed JSON result.
4. Confirm `ACTIVE\diagnostics\20260515_02_diagnostic-bundle.zip` exists.

Expected result: the diagnostic bundle exports without requiring hardware.

## Manual acceptance observations

Record the following if you send results back:

| Item | Observation |
|---|---|
| App launched from `RUN_UDAQ.bat` |  |
| `Testing` menu visible |  |
| Smoke test result |  |
| Sandbox demo result |  |
| Apply/rollback result |  |
| Diff report result |  |
| Visible shell wiring audit result |  |
| Diagnostic bundle path |  |
| Any unexpected warning/error text |  |

## Boundary confirmation

Sprint 1 is accepted only if the evidence continues to state that sandbox apply does not execute live, does not write hardware outputs, and does not promote mappings into authoritative live runtime state.
