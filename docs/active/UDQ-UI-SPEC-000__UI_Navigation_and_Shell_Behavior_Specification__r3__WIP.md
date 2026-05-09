---
document_id: UDQ-UI-SPEC-000
title: UI Navigation and Shell Behavior Specification
revision: r4
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-MOD-001
  - UDQ-PROF-SPEC-001
supersedes:
  - UDQ-UI-SPEC-000__UI_Navigation_and_Shell_Behavior_Specification__r2__WIP.md
revision_history:
  - revision: r4
    date: 2026-03-28
    summary: Docs-only UI alignment pass. Renamed the primary workspaces to Operate, Logic Designer, Session Review, and System; made the primary control column dockable with right-side default; and added explorer, legend, graph-setup, and restore-default-layout behavior.
  - revision: r2
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Added explicit shell regions, top-bar and lower-pane expectations, layout presets, left/right dock persistence, and workspace-context toolbar behavior.
  - revision: r1
    date: 2026-03-22
    summary: Added bounded implementation notes for shell controller behavior, trace visibility, overlay state, and return-to-live posture.
---

# UI Navigation and Shell Behavior Specification [SEC:UDQ-UI-SPEC-000::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-000::1]

This document defines shell navigation, persistent regions, docking behavior, workspace switching, and layout persistence for the UniversalDAQ desktop application.

## 2. Shell Regions [SEC:UDQ-UI-SPEC-000::2]

The shell shall expose these persistent regions:
- **top status strip**
- **workspace switcher**
- **central work surface**
- **primary control dock**
- **optional explorer dock**
- **lower evidence pane**
- **optional inspector / trace inspector**

## 3. Top Status Strip [SEC:UDQ-UI-SPEC-000::3]

The top strip shall always remain visible and shall show, at minimum:
- current workspace
- live/replay/fake/historical posture
- current connection or backend state
- current control posture (`view_only`, `armed_control`, `engineering`)
- selected device or session context where applicable
- active alarm summary


## 3A. Standard Menu Bar [SEC:UDQ-UI-SPEC-000::3A]

The shell shall expose a standard desktop program menu bar with, at minimum:
- File
- View
- Workspace
- Mode
- Settings
- Help

These menus shall remain available regardless of the active workspace. User-Demo mode shall be reachable from the menu bar without relying on hidden developer-only entry points.

## 4. Workspace Navigation [SEC:UDQ-UI-SPEC-000::4]

The shell shall provide direct navigation to:
- Operate
- Logic Designer
- Session Review
- System

Workspace switching shall preserve context where safe, but shall never blur live and historical truth states.

## 5. Central Work Surface [SEC:UDQ-UI-SPEC-000::5]

The central work surface is the visual center of gravity.
- In Operate, it is the graph/value surface.
- In Logic Designer, it is the design canvas and structured editor surface.
- In Session Review, it is the historical session detail and lightweight report surface.
- In System, it is the device/settings/diagnostics content surface.

## 6. Primary Control Dock [SEC:UDQ-UI-SPEC-000::6]

### 6.1 Docking rule [SEC:UDQ-UI-SPEC-000::6.1]
The primary control column shall be dockable on the left or right and shall **default to the right**.

### 6.2 Expected content [SEC:UDQ-UI-SPEC-000::6.2]
Depending on workspace, the primary dock may host:
- device/session controls
- signal/channel selection
- trace and legend controls
- notes and quick actions
- selected block/trace inspector content
- report/export actions

### 6.3 Persistence rule [SEC:UDQ-UI-SPEC-000::6.3]
The dock position, visibility, and size shall persist across launches unless the user chooses Restore Default Layout.

## 7. Explorer Dock [SEC:UDQ-UI-SPEC-000::7]

The shell may expose a secondary explorer dock containing Device Explorer, Signal Explorer, Logic Module Explorer, Favorites, or Saved Sets. The explorer dock may live on the left, right, or as a floating panel according to layout preference.

## 8. Lower Evidence Pane [SEC:UDQ-UI-SPEC-000::8]

The lower pane shall host:
- event and alarm log
- diagnostics/status output
- recent action audit entries
- watch values
- validation/simulation output
- note and annotation summaries where appropriate

The lower pane shall be collapsible, resizable, and restorable.

## 9. Inspectors [SEC:UDQ-UI-SPEC-000::9]

The shell may host contextual inspectors such as:
- trace inspector
- selected signal detail
- selected device point detail
- selected logic-block detail
- session detail inspector

The inspector is a supporting surface, not the only place where critical truth is visible.

## 10. Layout Management [SEC:UDQ-UI-SPEC-000::10]

The shell shall support:
- layout persistence
- named layout presets
- restore default layout
- workspace-aware layout restoration
- safe startup behavior when a prior layout references currently unavailable panels

## 11. Historical versus Live Navigation Rule [SEC:UDQ-UI-SPEC-000::11]

Historical review may occur in the same shell, but the shell shall make it visually obvious when the user is in:
- live operation
- historical session review
- simulation/replay
- restored historical continuity

No historical or restored panel state shall silently imply current live truth.

## 12. Graph and Legend Access Rule [SEC:UDQ-UI-SPEC-000::12]

Graph setup management, legend controls, and trace styling shall be reachable from the shell without forcing the user into a hidden settings-only path. Common actions such as show/hide trace, change trace appearance, switch axis, and save a graph setup shall be available through the graph-adjacent UI.

## 13. Human Review Focus [SEC:UDQ-UI-SPEC-000::13]

A reviewer should quickly confirm that:
- the shell has one persistent top status strip
- the primary control column defaults right but docks left or right
- the graph/value area remains visually central in Operate
- explorer, evidence, and inspector surfaces are separate and optional rather than baked into one fixed column
- layout persistence includes a restore-default action

## 2A. Persistent Information Bar [SEC:UDQ-UI-SPEC-000::2A]

The shell shall expose a **persistent information bar** across the top edge of the application window. This bar is always visible in Operate, Logic Designer, Session Review, and System workspaces.

The persistent information bar shall include, at minimum:
- active workspace label
- runtime posture label (`live`, `replay`, `fake`, or `user-demo`)
- connection or device lifecycle label
- control posture label (`view_only`, `armed_control`, or `engineering`)
- alarm summary label
- selected device label
- active signal label
- freshness label
- restored historical-context label when applicable

When User-Demo mode is active, the information bar shall display an unmistakable mode badge such as `USER-DEMO` and shall communicate that outputs are demo-only.

## 2B. Docking Default [SEC:UDQ-UI-SPEC-000::2B]

The primary control dock shall default to the **right** side of the shell. The operator may re-dock it on the left, float it, or restore the default layout. Persisted layout state shall remember the user-selected dock side without removing the availability of the canonical right-side default.

## 5A. User-Demo Entry [SEC:UDQ-UI-SPEC-000::5A]

The shell shall expose a menu-entered **User-Demo** posture as part of the runtime-mode selection model. User-Demo shall be reachable from a stable menu path and shall not be hidden as a developer-only feature. Entering User-Demo shall preserve shell layout while switching the active runtime posture, available scenarios, and simulated signal sources.

## 2026-03-28 implementation addendum — shell ergonomics and saved views
- The `View` menu shall expose `Restore Default Layout`, `Save Current View…`, `Manage Saved Views…`, and `Reset Panel Sizes`.
- The shell shall treat Device Explorer visibility, Signal Explorer visibility, Trace Inspector visibility, Notes visibility, control-column visibility, and events-console visibility as first-class persisted shell state.
- Device Explorer and Signal Explorer shall remain conceptually distinct even when they reference the same underlying signal identity.

## 2026-03-29 implementation addendum — splitter-first shell policy and safe geometry
- The outer shell should be governed by a left/center/right splitter with a lower center evidence pane rather than relying on dock geometry alone for the main skeleton.
- Restored window geometry shall be clamped to the active screen's available bounds before being applied.
- Layout state shall carry a schema version so stale geometry can be discarded deterministically.
- Workspace graph presentation defaults shall be explicit: Operate and Session Review prefer primary graph presentation; Logic Designer and System may prefer compact picture-in-picture presentation or hidden graph posture.


## 2026-03-30 documentation closeout addendum — persistent information bar and graph recovery
- The persistent information bar shall expose stable sections for `Mode`, `Device/Selection`, `Freshness`, `Access`, `Graph`, `Control`, and `Alarms`.
- Semantic color meanings are fixed across the package: green = healthy/ready/live, blue = informational or active mode, amber = degraded/limited/guarded, red = fault/disconnected/ESD, gray = inactive/none/hidden.
- Color shall never be the only cue. Each chip or badge shall retain text and, where useful, iconography.
- The `Graph` section shall expose `Primary`, `PiP`, and `Hidden` as direct recovery controls so hiding PiP never forces a full layout reset.
- When the selected device changes, the shell shall route that context into a device-scoped detail surface rather than requiring the user to piece the device picture together across multiple unrelated panels.
