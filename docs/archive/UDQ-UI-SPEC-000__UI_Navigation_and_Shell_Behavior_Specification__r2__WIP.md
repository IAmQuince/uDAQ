---
document_id: UDQ-UI-SPEC-000
title: UI Navigation and Shell Behavior Specification
revision: r2
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-MOD-001
  - UDQ-PROF-SPEC-001
supersedes:
  - UDQ-UI-SPEC-000__UI_Navigation_and_Shell_Behavior_Specification__r1__WIP.md
revision_history:
  - revision: r2
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Added explicit shell regions, top-bar and lower-pane expectations, layout presets, left/right dock persistence, and workspace-context toolbar behavior.
  - revision: r1
    date: 2026-03-22
    summary: Added bounded implementation notes for shell controller behavior, trace visibility, overlay state, and return-to-live posture.
  - revision: r0
    date: 2026-03-21
    summary: Defines shell, docking, workspace switching, and layout behavior.
---
# UI Navigation and Shell Behavior Specification [SEC:UDQ-UI-SPEC-000::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-000::1]

This document defines the application shell, navigation model, docking behavior, and layout persistence rules for the primary UniversalDAQ UI.

## 2. Shell Doctrine [SEC:UDQ-UI-SPEC-000::2]

The shell shall maintain a graph-dominant operating posture with dockable tooling, an evidence-oriented lower pane, and optional detail inspection without losing workspace identity.

## 3. Primary Shell Regions [SEC:UDQ-UI-SPEC-000::3]

The shell shall contain the following primary regions:

1. **Top status-and-actions bar**  
   Workspace selection, live/review state, backend/device health summary, session/profile identity, alarm summary, quick return-to-live, search/jump, and compact quick actions.

2. **Main work region**  
   Graph surface or primary task surface for the active workspace.

3. **Primary dock rail**  
   User-dockable on the left or right side. Hosts compact high-value tools for the active workspace.

4. **Lower evidence pane**  
   Events, alarms, command outcomes, validation, diagnostics, notes, and selected-range evidence.

5. **Optional inspector/detail pane**  
   Focused object detail, dependencies, usage, runtime status, or audit detail.

## 4. Navigation Behavior [SEC:UDQ-UI-SPEC-000::4]

Top-level workspace switching shall preserve local context where possible. Returning to a workspace shall restore the last local page posture unless current authority, connectivity, or capability prevents exact restoration.

The top-level workspace set is:
- Run
- Control
- Review
- System

The shell may expose contextual second-level navigation within a workspace, but the top-level workspace identity shall remain obvious.

## 5. Docking Rules [SEC:UDQ-UI-SPEC-000::5]

- The primary dock rail shall support left-docked and right-docked placement.
- Dock placement shall be persisted as part of layout/profile preferences.
- The lower pane shall support shown, hidden, resized, and tabbed states.
- The inspector may be docked, hidden, or collapsed.
- Layout restore shall not imply restored runtime truth.

## 6. Layout Presets [SEC:UDQ-UI-SPEC-000::6]

The shell should support named layout presets such as:
- Operate
- Develop
- Review
- Debug

These presets may modify which regions are expanded, but shall not silently change active machine state or control authority.

## 7. Toolbar Behavior [SEC:UDQ-UI-SPEC-000::7]

The top bar shall remain high-value and uncluttered. It shall favor:
- status
- session identity
- quick workspace jumps
- alarm and evidence entry points
- quick return-to-live
- search and jump-to-object

Workspace-specific editing actions such as Validate, Simulate, Compare Draft vs Deployed, Apply, or Roll Back should primarily live in a contextual workspace toolbar rather than overloading the global top bar.

## 8. Lower Pane Behavior [SEC:UDQ-UI-SPEC-000::8]

The lower pane is the evidence spine. It shall:
- remain available from all major workspaces
- support tabbed evidence categories
- reflect selection context when appropriate
- preserve user context while investigating what happened
- permit direct navigation from evidence back to the authored object or graph range where appropriate

## 9. Startup and Restore [SEC:UDQ-UI-SPEC-000::9]

The shell may restore:
- dock placement
- pane visibility
- selected workspace
- selected tabs
- graph posture
- inspector posture

The shell shall not imply that:
- restored live mode is current truth before reconciliation
- restored draft state is deployed state
- restored command posture equals current backend permission

## 10. Return-to-Live Behavior [SEC:UDQ-UI-SPEC-000::10]

Any review or explore posture that detaches from live follow shall have an obvious and durable route back to live. The route back to live shall:
- restore the current live time horizon
- restore active live trace selection as configured
- remove detached-review indicators only when live follow is actually re-established

## 11. Bounded Implemented Slice [SEC:UDQ-UI-SPEC-000::11]

The current bounded code slice already contains shell/session and graph-mode state scaffolding. The fuller shell defined here remains the target UI contract rather than a claim of complete current GUI implementation.

## 12. Human Review Focus [SEC:UDQ-UI-SPEC-000::12]

A reviewer should quickly confirm that the shell doctrine preserves:
- graph dominance
- left/right dock preference
- a persistent evidence spine
- contextual authoring tools without toolbar bloat
- explicit return-to-live behavior
- honest restore behavior
