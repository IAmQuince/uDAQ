# Retention and Active-Lane Ledger — 2026-03-27

**CANONICAL CURRENT SUPPORTING LEDGER FOR PACKAGE `UDQ-PKG-20260327-RETENTION-AUDIT-ACTIVE-LANE-SLIMMING-R01`**

## Purpose
Make the cold-path artifact story explicit and bounded enough for review. This ledger records what was kept active, what was demoted to archive summary, and why.

## Retention rules applied in this pass
- keep exactly one canonical active acceptance run under `proof/acceptance/`
- preserve superseded acceptance runs only as archive summaries unless a later package explicitly reactivates them
- keep current front-door release surfaces at `docs/release/` top-level
- move superseded review-start and sprint-summary surfaces behind `docs/release/history/`
- keep only current-package audit artifacts in `audit_reports/active/`; move stale dated audit outputs to `audit_reports/archive/`

## Active vs historical routing
| Artifact class | Active location | Historical location | Rule applied in this pass |
|---|---|---|---|
| canonical acceptance run | `proof/acceptance/` | `proof/archive/acceptance/` | exactly one active run retained |
| superseded acceptance run | n/a | `proof/archive/acceptance/` | summary-only archive retained; bulky raw subtree removed from active package |
| current review entry | `docs/release/` | `docs/release/history/` | exactly one canonical active review entry |
| superseded review-start docs | n/a | `docs/release/history/` | moved out of active front door |
| active audit artifacts | `audit_reports/active/` | `audit_reports/archive/` | stale outputs moved to archive; current outputs regenerated |

## Before/after snapshot
| Area | Before | After | Effect |
|---|---:|---:|---|
| `proof/acceptance/` file count | 1311 | 659 | active acceptance lane cut to one canonical run |
| `docs/release/` top-level file count | 31 | 10 | active front door reduced to current surfaces |
| active acceptance runs | 2 | 1 | duplicate active evidence removed |
| archived acceptance summaries | 0 | 1 | historical traceability preserved in lighter form |

## Canonical active proof lane
- active acceptance run: `20260327_025549`
- active proof manifest: `proof/20260327_01_retention-audit-active-lane-slimming__active-proof-lane-manifest.md`

## Historical summary retention
- archived acceptance summary: `proof/archive/acceptance/20260327_023724/`
- retained historical files: `acceptance_report.md`, `acceptance_report.json`, manifest files
- omitted from active package lane: subordinate replay/reviewability/fault/repeatability/raw subtree files from the superseded run
