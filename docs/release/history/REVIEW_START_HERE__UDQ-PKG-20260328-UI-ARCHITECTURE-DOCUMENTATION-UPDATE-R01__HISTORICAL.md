# Review Start Here — UI Architecture Documentation Update — 2026-03-28

**HISTORICAL ENTRY DOCUMENT — SUPERSEDED BY PACKAGE `UDQ-PKG-20260328-VISIBLE-OPERATOR-SHELL-AND-DEMO-EMBODIMENT-R01`**

## Package identity
- Package ID: `UDQ-PKG-20260328-UI-ARCHITECTURE-DOCUMENTATION-UPDATE-R01`
- Package slug: `ui-architecture-documentation-update`
- Package date: `2026-03-28`
- Run ID: `R01`
- Current pass: `No-code UI architecture documentation update`
- Entry role: `review_entry`
- Entry status: `historical`
- Supersedes: `UDQ-PKG-20260327-SESSION-REVIEW-AND-LIGHTWEIGHT-REPORTING-R01`


## Mandatory classification rule for this review
- `ACTIVE`, `ARCHIVED`, and `RECORD` are governed states carried by the document system, not casual adjectives.
- legacy filename suffixes like `__WIP` are not authoritative by themselves.
- review this package by controlled status, authority, and registry placement first; do not infer package truth from filename-era residue alone.

## What this package is
This package is a docs-only alignment pass that records the current UI decisions before visible GUI implementation proceeds. It locks workspace naming, shell docking behavior, signal browsing doctrine, graphing flexibility, logic-designer separation, trace style/legend/alarm-overlay expectations, and persistence/performance rules for the future operator shell.

## Read these first
1. `docs/release/EXEC_SUMMARY.md`
2. `docs/release/RELEASE_NOTES.md`
3. `docs/release/20260328_00_ui-architecture-documentation-update__implementation-summary.md`
4. `docs/release/20260328_00_ui-architecture-documentation-update__validation-summary.md`
5. `docs/active/UDQ-UI-ARCH-001__UI_Functional_Architecture__r3__WIP.md`
6. `docs/active/UDQ-UI-SPEC-000__UI_Navigation_and_Shell_Behavior_Specification__r3__WIP.md`
7. `docs/active/UDQ-UI-SPEC-004__Graphing_History_Review_and_Live_Trace_Specification__r4__WIP.md`
8. `docs/active/UDQ-UI-SPEC-006__Logic_Designer_Workspace_and_Control_Authoring_Model__r1__WIP.md`
9. `docs/active/UDQ-PROF-SPEC-001__Profiles_Persistence_Autosave_and_Restore_Specification__r4__WIP.md`
10. `docs/handbook/NEXT_ACTIONS.md`

## What to verify quickly
- the shell now defaults the primary control dock to the right while preserving left/right docking flexibility
- the workspaces are Operate, Logic Designer, Session Review, and System
- graphing is explicitly allowed for any plottable signal through curated views
- trace identity, binding, and presentation are explicitly separated
- trace styling, legend behavior, alarm severity overlays, and saved graph setups are documented as first-class persisted concerns
- pyqtgraph is retained, but performance responsibility remains architectural rather than delegated entirely to the library

## What this package is not
- not a delivered widget-level GUI shell
- not a code implementation of the dockable operator window
- not a graph-engine spike
- not a control-logic implementation pass


- Superseded by: `UDQ-PKG-20260328-VISIBLE-OPERATOR-SHELL-AND-DEMO-EMBODIMENT-R01`
