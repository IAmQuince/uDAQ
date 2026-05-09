---
document_id: UDQ-UI-ARCH-001
title: UI Functional Architecture
revision: r3
status: WIP
document_class: ui_architecture
owner: UniversalDAQ
depends_on:
  - UDQ-ARCH-NAR-001
  - UDQ-ARCH-NAR-002
  - UDQ-UI-NAR-001
  - UDQ-UI-MOD-001
  - UDQ-UI-SPEC-000
  - UDQ-UI-SPEC-001
  - UDQ-UI-SPEC-006
supersedes:
  - UDQ-UI-ARCH-001__UI_Functional_Architecture__r2__WIP.md
---

# UI Functional Architecture [SEC:UDQ-UI-ARCH-001::0]

## Revision History [SEC:UDQ-UI-ARCH-001::0.1]
- r3: Docs-only UI alignment pass. Reframed the shell around Operate, Logic Designer, Session Review, and System workspaces; made the primary control column dockable with right-side default; formalized Device Explorer versus Signal Explorer versus Logic Module Explorer; and reserved a flexible graphing model in which any plottable signal may be rendered through curated views.
- r2: Docs-only UI refinement pass. Reorganized the architecture around Run, Control, Review, and System workspaces; formalized the evidence spine and optional inspector; and reframed the sequence surface as a supporting control-authoring feature rather than the main organizing metaphor.
- r1: Initial functional architecture and subsystem decomposition pass.

## 1. Purpose [SEC:UDQ-UI-ARCH-001::1]

This document defines the functional architecture of the UniversalDAQ UI. It governs how the UI is decomposed into major workspaces, shell regions, explorer surfaces, graphing services, control-authoring services, and operator-facing behavior boundaries.

## 2. Scope [SEC:UDQ-UI-ARCH-001::2]

This architecture covers:
- the primary application shell
- workspace decomposition
- dock and explorer behavior
- operator graphing and review architecture
- logic-designer architecture
- diagnostics, persistence, and settings surfaces
- cross-cutting services such as trace styling, graph setups, and layout persistence

## 3. Architectural Intent [SEC:UDQ-UI-ARCH-001::3]

The UI architecture shall support a universal engineering workflow in which the user can move cleanly between:
- live operation and observation
- logic authoring, simulation, and live monitoring
- historical session review and lightweight reporting
- device/system onboarding and configuration

The architecture shall avoid:
- device-specific shell assumptions
- forcing logic editing into the same conceptual space as live operation
- mixing historical review with live truth
- flattening raw hardware names, logical signals, and derived variables into one ambiguous browser

## 4. Top-Level Functional Decomposition [SEC:UDQ-UI-ARCH-001::4]

The top-level functional decomposition is:
1. **Shell and layout framework**
2. **Operate workspace**
3. **Logic Designer workspace**
4. **Session Review workspace**
5. **System workspace**
6. **Cross-cutting explorer, graphing, persistence, and diagnostics services**

## 5. UI Shell and Window Framework [SEC:UDQ-UI-ARCH-001::5]

### 5.1 Role [SEC:UDQ-UI-ARCH-001::5.1]
The shell hosts the graph-centered work area, persistent status strip, dockable tooling, explorer surfaces, lower evidence pane, optional inspector, and workspace navigation.

### 5.2 Responsibilities [SEC:UDQ-UI-ARCH-001::5.2]
The shell shall provide:
- persistent top-level workspace navigation
- a top status strip that always shows current mode, connection/session truth, control posture, and alarm summary
- a main work area centered on graphing or the current designer/review surface
- a primary control column that is dockable on the left or right and defaults to the **right**
- an optional secondary explorer dock that may host Device Explorer, Signal Explorer, or Logic Module Explorer
- a lower evidence pane for events, alarms, diagnostics, notes, watch values, and validation output
- layout persistence, named layout presets, and a restore-default-layout action

### 5.3 Architectural Rule [SEC:UDQ-UI-ARCH-001::5.3]
The shell shall preserve context while making live, historical, and authoring boundaries explicit. The same application may host all three, but it shall not silently collapse their truth boundaries merely because the same graphing substrate or dock widgets are reused.

## 6. Operate Workspace [SEC:UDQ-UI-ARCH-001::6]

### 6.1 Role [SEC:UDQ-UI-ARCH-001::6.1]
Operate is the live bench workspace.

### 6.2 Responsibilities [SEC:UDQ-UI-ARCH-001::6.2]
Operate shall provide:
- the central live graphing surface
- current values and quality/freshness state
- active signal/channel context
- current protections/interlocks summary
- bounded command-capable controls where authorized
- quick access to notes, diagnostics, and recent events
- fast switching among curated signal views such as Hardware, Raw, Logical, Derived, Control, Favorites, and Saved Sets

### 6.3 Architectural Rule [SEC:UDQ-UI-ARCH-001::6.3]
Operate shall allow any plottable signal to be graphed, but through curated browsing lenses rather than one undifferentiated object tree.

## 7. Logic Designer Workspace [SEC:UDQ-UI-ARCH-001::7]

### 7.1 Role [SEC:UDQ-UI-ARCH-001::7.1]
Logic Designer is the dedicated authoring workspace for mappings, transforms, rules, sequences, interlocks, state logic, and safe output preparation.

### 7.2 Responsibilities [SEC:UDQ-UI-ARCH-001::7.2]
Logic Designer shall provide:
- a central authoring canvas and/or structured editor
- a block palette and reusable module/subflow inventory
- an inspector for selected sources, transforms, logic blocks, and sinks
- test, simulation, and live-monitor posture controls
- watch values and validation output in a lower pane
- clear distinction between draft, simulated, monitored-live, and armed/apply posture

### 7.3 Architectural Rule [SEC:UDQ-UI-ARCH-001::7.3]
Logic Designer is separate from Operate as a workspace, but it remains inside the same shell so the user can make changes, simulate control logic, monitor results, and compare effects without context loss.

## 8. Session Review Workspace [SEC:UDQ-UI-ARCH-001::8]

### 8.1 Role [SEC:UDQ-UI-ARCH-001::8.1]
Session Review is the historical, reporting, and forensic workspace.

### 8.2 Responsibilities [SEC:UDQ-UI-ARCH-001::8.2]
Session Review shall provide:
- bounded recent-session review
- historical session detail panels
- lightweight report generation
- compact historical signal previews
- access to notes, action digests, alarm posture, and flight-record references

### 8.3 Architectural Position [SEC:UDQ-UI-ARCH-001::8.3]
Session Review is distinct from Operate even when it reuses the same graphing substrate. Historical previews shall remain clearly historical and never impersonate live updating traces.

## 9. System Workspace [SEC:UDQ-UI-ARCH-001::9]

### 9.1 Role [SEC:UDQ-UI-ARCH-001::9.1]
System is the configuration, diagnostics, and service workspace.

### 9.2 Responsibilities [SEC:UDQ-UI-ARCH-001::9.2]
System shall provide:
- device discovery and onboarding
- capability and identity review
- bindings and point maps where appropriate
- diagnostics and dependency visibility
- settings, profiles, autosave, and persistence controls
- graph setup and style-management access when appropriate

## 10. Explorer Architecture [SEC:UDQ-UI-ARCH-001::10]

The UI shall treat browsing as a first-class architectural concern.

### 10.1 Device Explorer [SEC:UDQ-UI-ARCH-001::10.1]
Device Explorer presents raw hardware- and adapter-oriented objects grouped by adapter family, device instance, and point/channel.

### 10.2 Signal Explorer [SEC:UDQ-UI-ARCH-001::10.2]
Signal Explorer presents normalized logical signals, derived variables, and operator-facing signal groupings.

### 10.3 Logic Module Explorer [SEC:UDQ-UI-ARCH-001::10.3]
Logic Module Explorer presents reusable blocks, groups, subflows, and control modules.

### 10.4 Separation Rule [SEC:UDQ-UI-ARCH-001::10.4]
Raw hardware, logical signals, and control modules shall be browseable in the same shell but shall not be collapsed into one ambiguous namespace.

## 11. Graphing and Trace Architecture [SEC:UDQ-UI-ARCH-001::11]

### 11.1 Role [SEC:UDQ-UI-ARCH-001::11.1]
Graphing is the central evidence surface shared across Operate and Session Review, and partially reused inside Logic Designer for simulation and live-monitor explainability.

### 11.2 Responsibilities [SEC:UDQ-UI-ARCH-001::11.2]
The graphing architecture shall support:
- live follow, sliding window, historical review, and replay/simulation differentiation
- plotting of any plottable signal class through curated views
- saved graph setups and view presets
- interactive legend behavior
- per-trace styling and alarm-aware overlays
- truthful multiresolution rendering for long ranges and many traces

### 11.3 Central Rule [SEC:UDQ-UI-ARCH-001::11.3]
Trace identity, trace binding, and trace presentation shall remain separate concerns so the same signal may appear in different graph setups with different labels, styles, and axis assignments without losing stable signal identity.

## 12. Lower Evidence Pane [SEC:UDQ-UI-ARCH-001::12]

The lower pane is the shared evidence spine for events, alarms, diagnostics, notes, watch values, validation output, and selected-range evidence.

## 13. Cross-Cutting Services [SEC:UDQ-UI-ARCH-001::13]

The shell shall include cross-cutting services for:
- signal registry and signal-reference resolution
- graph setup management
- trace-style persistence
- diagnostics and flight-record generation
- settings/profile persistence with autosave controls
- search, filtering, favorites, and recent objects

## 14. Human Review Focus [SEC:UDQ-UI-ARCH-001::14]

A reviewer should quickly confirm that:
- the primary workspaces are Operate, Logic Designer, Session Review, and System
- the primary control dock defaults to the right but remains dockable left or right
- device browsing, signal browsing, and logic-module browsing are separate experiences
- the logic-authoring surface is a separate workspace inside the same shell
- graphing is flexible but performance-aware and truth-preserving

## 2A. Persistent Top Information Bar [SEC:UDQ-UI-ARCH-001::2A]

The shell architecture includes a persistent top information bar that remains present across all primary workspaces. The information bar is part of the shell truth surface and shall summarize workspace, runtime posture, connection/device state, control posture, alarm posture, selected device/signal identity, freshness, and restored historical context.

## 2B. User-Demo Runtime Posture [SEC:UDQ-UI-ARCH-001::2B]

User-Demo is a first-class runtime posture of the shell architecture. It is not a hidden developer harness. User-Demo shall provide curated pseudo-live scenarios that showcase graphing, trace styling, alarm overlays, logic authoring, and pseudo control interaction while remaining clearly segregated from live runtime authority.
