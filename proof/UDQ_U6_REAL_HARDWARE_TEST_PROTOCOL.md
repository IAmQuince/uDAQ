# UDQ U6 Real Hardware Test Protocol

## Goal
Run one guided hardware sequence and return a small evidence bundle rather than many copy/paste snippets.

## Tool
- `tools\dev\run_u6_field_test_harness.bat`

## Sequence
1. start with the U6 connected and launch the harness
2. let the baseline capture complete
3. unplug the U6 when prompted and continue
4. reconnect the U6 when prompted and continue
5. send back the generated bundle directory from `proof\field_tests\...`

## Expected returned files
- `...__summary.txt`
- `...__events.csv`
- `...__diagnostics.json`
- `...__smoke.txt`

## What the reviewer can determine
- requested vs entered mode
- lifecycle state by phase
- startup classification by phase
- failure and reconnect counters
- runtime/alarm/event context during the test window
