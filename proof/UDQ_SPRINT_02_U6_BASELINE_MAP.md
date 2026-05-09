# UDQ Sprint 2 — U6 Baseline Map

## Pre-sprint starting point
Before this sprint, the bounded real U6 line already existed, but its runtime truth was too coarse.

## What existed already
- real U6 discovery and activation through `universaldaq_labjack`
- three analog inputs in the bounded proof slice
- simulated U6 fallback path
- smoke and diagnostic scripts
- reconnect/degraded proof language at the package level

## Main baseline weaknesses
- no explicit structured lifecycle-state snapshot from the adapter itself
- startup classification was implicit rather than explicit
- read failure truth was mostly a single error summary
- hardware testing still leaned too much on manual review of console output

## What Sprint 2 targets
- explicit adapter lifecycle state
- explicit startup classification
- bounded reconnect/disconnect counters
- richer diagnostics in smoke/diag outputs
- a file-based field-test evidence bundle
