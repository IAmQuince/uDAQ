# UDQ U6 Diagnostics Inventory

## Adapter-level additions
- lifecycle state
- startup classification
- reconnect attempts
- disconnect count
- successful poll count
- last failure reason
- last close reason
- last success / failure / transition timestamps

## Tooling surfaces updated
- `run_labjack_u6_smoke.py`
- `run_u6_diag.py`
- `run_u6_live_value_smoke.py`
- `run_u6_field_test_harness.py`

## Reviewer value
A reviewer can now tell whether the run was healthy, degraded, disconnected, or recovered without reading code.
