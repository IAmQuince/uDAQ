# Review Start Here — Visible Operator Shell and Demo Embodiment — 2026-03-28

**CANONICAL CURRENT REVIEW ENTRY FOR PACKAGE `UDQ-PKG-20260328-VISIBLE-OPERATOR-SHELL-AND-DEMO-EMBODIMENT-R01`**

## Package identity
- Package ID: `UDQ-PKG-20260328-VISIBLE-OPERATOR-SHELL-AND-DEMO-EMBODIMENT-R01`
- Package slug: `visible-operator-shell-and-demo-embodiment`
- Package date: `2026-03-28`
- Run ID: `R01`
- Current pass: `Visible operator shell and demo embodiment`
- Entry role: `review_entry`
- Entry status: `canonical`
- Supersedes: `UDQ-PKG-20260328-LAUNCHABLE-OPERATOR-SHELL-AND-USER-DEMO-FOUNDATION-R01`


## Mandatory classification rule for this review
- `ACTIVE`, `ARCHIVED`, and `RECORD` are governed states carried by the document system, not casual adjectives.
- legacy filename suffixes like `__WIP` are not authoritative by themselves.
- review this package by controlled status, authority, and registry placement first; do not infer package truth from filename-era residue alone.

## What this package is
This package delivers the first launchable visible Qt shell for UniversalDAQ. It embodies the persistent top information bar, standard desktop menu bar, right-default dock model, User-Demo mode, a visible Operate workspace with pyqtgraph, a visible Logic Designer foundation, and settings/layout persistence groundwork.

## Read these first
1. `docs/release/EXEC_SUMMARY.md`
2. `docs/release/RELEASE_NOTES.md`
3. `docs/release/20260328_02_visible-operator-shell-and-demo-embodiment__implementation-summary.md`
4. `docs/release/20260328_02_visible-operator-shell-and-demo-embodiment__validation-summary.md`
5. `docs/active/UDQ-UI-ARCH-001__UI_Functional_Architecture__r3__WIP.md`
6. `docs/active/UDQ-UI-SPEC-000__UI_Navigation_and_Shell_Behavior_Specification__r3__WIP.md`
7. `docs/active/UDQ-UI-SPEC-004__Graphing_History_Review_and_Live_Trace_Specification__r4__WIP.md`
8. `docs/active/UDQ-UI-SPEC-006__Logic_Designer_Workspace_and_Control_Authoring_Model__r1__WIP.md`
9. `docs/handbook/NEXT_ACTIONS.md`

## What to verify quickly
- the GUI launches as a visible desktop window when `PySide6` and `pyqtgraph` are installed
- the persistent top information bar remains visible across workspaces
- the menu bar exposes standard menus including File, View, Workspace, Mode, Settings, and Help
- User-Demo can be entered from the menu and drives pseudo-live graph and logic scenarios
- the right-default control dock, bottom event dock, and explorer dock persist layout state
- the graph supports early trace styling, interactive legend behavior, and alarm-aware overlays

## What this package is not
- not yet a live-hardware-first GUI proof
- not yet a complete multi-device operator shell
- not yet a full control-posture and safe-write embodiment
