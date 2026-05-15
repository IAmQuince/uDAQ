# 20260325_06 reconnect-path alignment correction — correction summary

## What changed
- Added reconnect-path alignment in `src/universaldaq_labjack/real_u6.py` so a live-session reconnect can prefer a fresh first-found acquisition with explicit serial verification before falling back to older reopen logic.
- Added `ReconnectAcquisitionError` and structured reconnect acquisition staging so reconnect failures are attributable to a narrow step.
- Added `prefer_direct_reacquire` to `RealLabJackU6Adapter` and enabled it from provider activation in `src/universaldaq_labjack/discovery.py` so the specimen-specific reacquisition detail stays inside the support pack.
- Added regression coverage proving that a previously failing reconnect can recover by using the verified probe path after a disconnect, while startup-open behavior remains intact.

## Why this matters to the main app
The change tightens the reusable lifecycle seam every future support pack will need:
- startup and reconnect now both flow through a proven acquisition/open contract,
- recovery is still earned only after a real first post-loss read,
- and the main app does not need LabJack-specific recovery policy in its core.

## Intended next validation order
1. `tools\dev\run_u6_direct_open_probe.bat`
2. `tools\dev\run_u6_startup_open_smoke.bat`
3. `tools\dev\run_u6_field_test_harness.bat`
