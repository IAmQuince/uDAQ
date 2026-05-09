# UniversalDAQ

**Controlled document**  
ID: UDQ-README-ROOT-001  
Status: ACTIVE  
Revision: r34  
Owner: Core Architecture  
Authority: PRIMARY  
Source docs: UDQ-GOV-LOG-001, UDQ-ARCH-NAR-001, UDQ-ARCH-NAR-002, UDQ-REQ-MAT-001, UDQ-GOV-REG-003

## Package identity
- Package ID: `UDQ-PKG-20260330-CONTROLLED-MAPPING-APPLY-PREFLIGHT-AND-REVIEW-PATH-R01`
- Package slug: `controlled-mapping-apply-preflight-and-review-path`
- Package date: `2026-03-30`
- Run ID: `R01`
- Package status: `active`
- Supersedes: `UDQ-PKG-20260330-CONTROLLER-BACKED-AUTHORITATIVE-MAPPING-READBACK-AND-DESKTOP-FIX-CLOSURE-R01`
- Canonical review entry: `docs/release/REVIEW_START_HERE__UDQ-PKG-20260330-CONTROLLED-MAPPING-APPLY-PREFLIGHT-AND-REVIEW-PATH-R01__ACTIVE.md`

## What this package is
This is a bounded runtime/control-boundary package that adds mapping proposal, preflight, review-summary, and prepared-request artifacts between shell-local draft edits and future controller-authorized mapping apply.

## What changed in this package
- Added structured mapping-change proposals from draft rows versus authoritative readback.
- Added preflight validation for missing/stale/unavailable/conflicting mapping changes.
- Added deterministic operator review summaries.
- Added dry-run/prepared-only mapping apply request artifacts.
- Added shell-facing review-panel states for pass, warning, blocked, and prepared-not-executed workflows.
- Added command-level timing instrumentation and sprint timing summaries for validation-efficiency analysis.
- Preserved the deferred boundary for live mapping apply and runtime-authoritative logic deployment.

## Start here
1. `docs/release/REVIEW_START_HERE__UDQ-PKG-20260330-CONTROLLED-MAPPING-APPLY-PREFLIGHT-AND-REVIEW-PATH-R01__ACTIVE.md`
2. `docs/release/EXEC_SUMMARY.md`
3. `docs/release/RELEASE_NOTES.md`
4. `docs/release/20260330_09_controlled-mapping-apply-preflight-and-review-path__implementation-summary.md`
5. `docs/release/20260330_09_controlled-mapping-apply-preflight-and-review-path__validation-summary.md`
6. `docs/architecture/MAPPING_APPLY_PREFLIGHT_AND_REVIEW_PATH__20260330_09.md`
7. `audit_reports/active/SPRINT_TIME_SUMMARY__20260330_09.md`
8. `docs/handbook/START_HERE.md`
9. `docs/handbook/AUDIT_AND_GOVERNANCE.md`
10. `docs/handbook/TESTS_AND_TOOLS.md`
11. `docs/handbook/NEXT_ACTIONS.md`

## Launch note
The visible shell still requires the optional UI dependencies. Install them with `python -m pip install -e .[ui]` and launch with `python -m tools.ui.launch_operator_shell` or `udq-visible-shell`.

## Scope note
This package adds controlled preflight/review/prepared-request behavior, not live apply authority. Draft shell edits remain non-authoritative and prepared requests are explicitly not executed.

## Save-point reconciliation note

The save-point reconciliation baseline remains part of this package history. Runtime apply, hardware-in-loop authority verification, and runtime logic deployment are still intentionally deferred.
