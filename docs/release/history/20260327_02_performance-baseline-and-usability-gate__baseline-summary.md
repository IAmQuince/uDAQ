# Performance Baseline Summary - 2026-03-27

**CANONICAL CURRENT SUPPORTING LEDGER FOR PACKAGE `UDQ-PKG-20260327-PERFORMANCE-BASELINE-AND-USABILITY-GATE-R01`**

## Purpose
This document records the measured baseline for the performance-baseline and usability-gate sprint. It replaces informal “speed” and “bloat” concerns with concrete timings, file counts, and size concentrations.

## Measured package-path timings

| Check | Result | External elapsed |
|---|---:|---:|
| package-entry validator | PASS | `4.55` s |
| document completeness validator | PASS | `4.45` s |
| document classification validator | PASS | `4.46` s |
| document impact validator | PASS | `4.20` s |
| active-lane boundedness validator | PASS | `4.42` s |
| Windows path-budget validator | PASS | `4.72` s |
| package build | PASS | `5.96` s |

## Measured runtime-path timings

| Check | Result | External elapsed | Additional detail |
|---|---:|---:|---|
| shell smoke | PASS | `5.08` s | max RSS about `312120` KB |
| runtime inventory | PASS | `5.09` s | max RSS about `311508` KB |
| focused pytest gate | PASS | `34.54` s | `13 passed in 25.76s` |

## Internal runtime metrics snapshot

| Metric | Value |
|---|---:|
| adapter count | `3` |
| discovered device count | `3` |
| projected points | `12` |
| discover avg | `1.158` ms |
| acquisition poll avg | `0.086` ms |
| acquisition capture avg | `0.022` ms |
| journal flush avg | `10.505` ms |
| processing cycle avg | `16.388` ms |

## Size and file-count concentration

| Area | File count | Size |
|---|---:|---:|
| proof | `395` | `5.57` MiB |
| registries | `100` | `1.75` MiB |
| src | `233` | `1.41` MiB |
| docs | `214` | `1.02` MiB |
| audit_reports | `134` | `0.96` MiB |
| tests | `231` | `0.51` MiB |
| tools | `122` | `0.47` MiB |

## Main findings
- the dominant storage concentration remains `proof/`, not the runtime code itself
- the dominant measured elapsed path in this sprint is the focused pytest gate rather than shell smoke or runtime inventory
- shell smoke and runtime inventory both complete in the low single-digit seconds externally
- internal runtime operations in the runtime inventory remain low-millisecond operations
- package build remains fast enough for continued iteration at the current package size

## Interpretation
The package is not showing a newly emergent catastrophic runtime-path blocker. The remaining drag is more in proof/history weight and validation/test cost than in the first-signal runtime path.
