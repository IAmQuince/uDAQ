---
document_id: UDQ-UI-SPEC-001
title: Workspace and Page Specifications
revision: r3
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-UI-ARCH-001
  - UDQ-UI-SPEC-000
  - UDQ-UI-SPEC-006
  - UDQ-DEV-SPEC-001
  - UDQ-SIG-SPEC-001
  - UDQ-OUT-SPEC-001
  - UDQ-LOG-SPEC-001
  - UDQ-SEQ-SPEC-001
  - UDQ-DIAG-SPEC-001
  - UDQ-HIS-SPEC-001
supersedes:
  - UDQ-UI-SPEC-001__Workspace_and_Page_Specifications__r1__WIP.md
revision_history:
  - revision: r3
    date: 2026-03-28
    summary: Docs-only UI alignment pass. Replaced Run/Control/Review naming with Operate/Logic Designer/Session Review, added explorer expectations, and clarified how device, signal, and logic-module browsing support the graphing and control-authoring workflows.
  - revision: r1
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Replaced the flat page inventory with a four-workspace contract and explicitly defined the Control workspace subtab set.
---
# Workspace and Page Specifications [SEC:UDQ-UI-SPEC-001::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-001::1]

This document defines the major workspaces in the primary UniversalDAQ UI and the required content expectations for each.

## 2. Workspace Set [SEC:UDQ-UI-SPEC-001::2]

The core workspace set is:
- Operate
- Logic Designer
- Session Review
- System

Each workspace answers a different family of user questions. No workspace shall exist without a clear primary question set.

## 3. Operate Workspace [SEC:UDQ-UI-SPEC-001::3]

Operate answers:
- What is happening now?
- What signal am I looking at?
- Is it live, stale, simulated, replayed, or historical?
- What may I do right now?

Operate shall keep visible:
- central live graph and current value surface
- active signal/channel context
- signal freshness and provenance context
- alarm summary and recent events
- quick notes and diagnostics access
- current graph setup / saved-view awareness

Operate shall support graphing of any plottable signal through curated browse modes such as Hardware, Raw, Logical, Derived, Control, Favorites, and Saved Sets.

## 4. Logic Designer Workspace [SEC:UDQ-UI-SPEC-001::4]

Logic Designer answers:
- How is behavior defined?
- How are hardware inputs, logical signals, derived variables, and writable sinks connected?
- What will happen if this logic is simulated or armed?
- Is the authored control system valid, testable, and deployable?

Logic Designer shall include, either as subtabs or equivalent surfaces:
- Overview
- Sources / Bindings
- Variables / Derived Signals
- Logic / Decisions
- Sequence
- Interlocks / Protections
- Outputs / Sinks
- Modes / States
- Test / Simulation / Monitor Live
- Audit / History

The user shall be able to inspect and modify logic in the same application used for operation, but in a dedicated designer workspace rather than mixed directly into the Operate screen.

## 5. Session Review Workspace [SEC:UDQ-UI-SPEC-001::5]

Session Review answers:
- What happened in prior sessions?
- What notes, alarms, actions, and posture changes matter for this review?
- What lightweight report should be generated or shared?

Session Review shall provide:
- recent-session inventory
- historical session detail view
- bounded visual preview / compact historical signal context
- notes, posture, and action digests
- lightweight report generation

## 6. System Workspace [SEC:UDQ-UI-SPEC-001::6]

System answers:
- What devices exist and how are they identified?
- What capabilities and bindings are known?
- What settings, autosave, profiles, and diagnostics exist?
- What graphing and persistence defaults are in force?

System shall provide:
- device onboarding/discovery
- capability and identity views
- diagnostics and health
- settings / persistence / autosave controls
- graph setup and style-management access where appropriate

## 7. Cross-Workspace Browsing [SEC:UDQ-UI-SPEC-001::7]

The shell shall expose at least these browsing experiences:
- Device Explorer for raw device points and writable sinks
- Signal Explorer for logical signals, variables, and derived signals
- Logic Module Explorer for reusable blocks, groups, and subflows

These explorers may live in shared docks, but their identities shall remain distinct.

## 8. Cross-Workspace Handoffs [SEC:UDQ-UI-SPEC-001::8]

Required handoffs include:
- Operate → Logic Designer for explaining or modifying the source of a plotted or alarming signal
- Operate → Session Review for historical correlation and reporting
- System → Logic Designer for newly discovered devices and point-to-signal binding
- Session Review → Operate via explicit return-to-live
- Logic Designer → Operate for monitoring the results of a simulated or live-monitored change

## 9. What Not to Do [SEC:UDQ-UI-SPEC-001::9]

The UI shall not:
- flatten all raw points, logical signals, variables, and control outputs into one ambiguous selection tree
- hide critical trust state in secondary popups only
- mix historical review and live operation into one unlabeled screen
- treat sequence as the only control-authoring concept
- force the user to leave the application to move between operation and logic design

## 10. Human Review Focus [SEC:UDQ-UI-SPEC-001::10]

A reviewer should quickly confirm that:
- the workspace structure is Operate / Logic Designer / Session Review / System
- device browsing and logical-signal browsing are separate experiences
- Logic Designer is a dedicated workspace inside the same shell
- Session Review is historical-only and visibly distinct from Operate

## 2A. User-Demo Availability [SEC:UDQ-UI-SPEC-001::2A]

User-Demo is a shell-level runtime posture rather than a standalone workspace. It shall be accessible while the operator is in Operate or Logic Designer and shall expose curated demo scenarios such as trace styling, alarm visualization, signal lineage, and pseudo-live logic/control flows.

## 3A. Operate Workspace in User-Demo [SEC:UDQ-UI-SPEC-001::3A]

When User-Demo is active, the Operate workspace shall:
- surface demo devices and demo signals through the same explorer and graph-selection seams used by other runtime postures
- support pseudo-live graph updates and alarm overlays
- allow the user to exercise trace styling, legend interaction, saved graph setups, and second-axis behavior without touching live hardware

## 4A. Logic Designer in User-Demo [SEC:UDQ-UI-SPEC-001::4A]

When User-Demo is active, the Logic Designer workspace shall support pseudo-live logic simulation using curated source, transform, and sink scenarios. The operator shall be able to edit logic, observe watch values, and inspect simulated outputs while the shell remains clearly marked as demo-only.

## 2026-03-28 implementation addendum — workspace defaults and mapping editor
- `Operate` shall favor Signal Explorer and trace-editing workflows.
- `Logic Designer` shall favor Signal Explorer and logic-authoring surfaces while leaving raw-device inspection secondary.
- `System` shall favor Device Explorer and the Mapping Editor as the explicit place where raw endpoints are bound to internal signals.
- `Session Review` may suppress explorer prominence and favor notes plus evidence/review surfaces.


## 2026-03-30 documentation closeout addendum — device-centered workflow
- **Device Explorer** is device-first navigation for devices, transports, raw endpoints, capability, and health.
- **Device I/O Inspector** in `System` is the canonical place to inspect all selected-device rows together: real inputs, real outputs, internal associations, virtual associations, tag/display names, capability/access posture, provenance/freshness, and authority state.
- **Signal Explorer** is a signal-first browser and consumption lens. It shall not become a second tagging editor or a second device browser.
- **Operate** and **Logic Designer** consume already-defined/tagged signals and device-I/O rows rather than becoming duplicate setup surfaces.
- Tag/display-name editing shall occur once against the canonical device-I/O row or canonical signal identity and then flow outward to other surfaces.
