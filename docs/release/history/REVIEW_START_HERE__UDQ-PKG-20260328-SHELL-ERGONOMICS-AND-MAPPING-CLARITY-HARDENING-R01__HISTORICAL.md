# Historical Review Entry — REVIEW_START_HERE__UDQ-PKG-20260328-SHELL-ERGONOMICS-AND-MAPPING-CLARITY-HARDENING-R01__ACTIVE

**HISTORICAL ENTRY DOCUMENT — superseded by `UDQ-PKG-20260330-GATE-REPAIR-AND-REVIEW-HARDENING-R01`**

- Historical source file: `REVIEW_START_HERE__UDQ-PKG-20260328-SHELL-ERGONOMICS-AND-MAPPING-CLARITY-HARDENING-R01__ACTIVE.md`
- Superseded by: `UDQ-PKG-20260330-GATE-REPAIR-AND-REVIEW-HARDENING-R01`

---

# Review Start Here — Shell Ergonomics and Mapping Clarity Hardening — 2026-03-28

**CANONICAL CURRENT REVIEW ENTRY FOR PACKAGE `UDQ-PKG-20260328-SHELL-ERGONOMICS-AND-MAPPING-CLARITY-HARDENING-R01`**

## Package identity
- Package ID: `UDQ-PKG-20260328-SHELL-ERGONOMICS-AND-MAPPING-CLARITY-HARDENING-R01`
- Package slug: `shell-ergonomics-and-mapping-clarity-hardening`
- Package date: `2026-03-28`
- Run ID: `R01`
- Current pass: `Shell ergonomics and mapping clarity hardening`
- Entry role: `review_entry`
- Entry status: `canonical`
- Supersedes: `UDQ-PKG-20260328-LIVE-RUNTIME-INTEGRATION-AND-SAFE-CONTROL-POSTURE-FOUNDATIONS-R01`

## What this package is
This package sharpens the visible shell: practical dock behavior, named quick views, a clear split between raw-device exploration and internal-signal exploration, and an explicit Mapping Editor that binds the two.

## Read these first
1. `docs/release/EXEC_SUMMARY.md`
2. `docs/release/RELEASE_NOTES.md`
3. `docs/release/20260328_04_shell-ergonomics-and-mapping-clarity-hardening__implementation-summary.md`
4. `docs/release/20260328_04_shell-ergonomics-and-mapping-clarity-hardening__validation-summary.md`
5. `docs/active/UDQ-UI-SPEC-000__UI_Navigation_and_Shell_Behavior_Specification__r3__WIP.md`
6. `docs/active/UDQ-UI-SPEC-001__Workspace_and_Page_Specifications__r2__WIP.md`
7. `docs/active/UDQ-UI-MOD-001__UI_State_and_Interaction_Model__r4__WIP.md`
8. `docs/active/UDQ-SIG-SPEC-001__Signals_and_Derived_Signals_Specification__r3__WIP.md`
9. `docs/active/UDQ-PROF-SPEC-001__Profiles_Persistence_Autosave_and_Restore_Specification__r4__WIP.md`

## What to verify quickly
- the View menu now claims save/manage view and panel reset actions
- Device Explorer and Signal Explorer are defined as distinct surfaces rather than relabeled copies
- the System workspace contains an explicit Mapping Editor surface and does not overload Logic Designer with binding work
- the events console is structured for timestamps, severity/category filtering, and search
- the package-entry tests now follow the active registry rather than hard-coded stale filenames
- the duplicate `udq_work/` wrapper is gone from the package root

## What this package is not
- not yet a transform-authoring or logic-authoring expansion
- not yet a broad live-runtime expansion
- not yet widget-runtime-verified in this environment because optional Qt dependencies are absent here
