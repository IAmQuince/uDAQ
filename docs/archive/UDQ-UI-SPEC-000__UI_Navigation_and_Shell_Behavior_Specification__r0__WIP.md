---
document_id: UDQ-UI-SPEC-000
title: UI Navigation and Shell Behavior Specification
revision: r0
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-MOD-001
  - UDQ-PROF-SPEC-001
revision_history:
  - revision: r0
    date: 2026-03-21
    summary: Defines shell, docking, workspace switching, and layout behavior.
---
# UI Navigation and Shell Behavior Specification {#ui-spec-000.s01}

## 1. Purpose [SEC:UDQ-UI-SPEC-000::1]

This document defines the application shell, navigation model, docking behavior, and layout persistence rules for the primary UniversalDAQ UI.

## 2. Shell Doctrine [SEC:UDQ-UI-SPEC-000::2]

The shell shall maintain a graph-dominant operating posture, with dockable control surfaces and lower review/service panes that can be shown, hidden, resized, and restored without losing workspace identity.

## 3. Primary Shell Regions [SEC:UDQ-UI-SPEC-000::3]

- Main graph and visualization region.
- Dockable vertical control rail.
- Lower pane for events, logs, diagnostics, and review tables.
- Optional inspector/detail pane for selected objects.

## 4. Navigation Behavior [SEC:UDQ-UI-SPEC-000::4]

Top-level workspace switching shall preserve the user’s current context where possible. Returning to a workspace shall restore the last known local page state unless current live authorization or capability prevents exact restoration.

## 5. Docking Rules [SEC:UDQ-UI-SPEC-000::5]

- Control rail shall support docked, resized, collapsed, and expanded states.
- Lower pane shall support collapsed and expanded review modes.
- Pop-out service/detail panes shall not become the sole path to critical runtime truth.

## 6. Startup and Restore [SEC:UDQ-UI-SPEC-000::6]

At startup, the shell shall restore layout and workspace arrangements from the most recent valid profile or autosave state while clearly separating restored UI arrangement from current live backend truth.

## 7. Modal Interaction Rules [SEC:UDQ-UI-SPEC-000::7]

Modal dialogs shall be reserved for actions requiring explicit confirmation or validation. Routine monitoring and state review shall remain non-modal.

## 8. Multi-Monitor and Pop-Outs [SEC:UDQ-UI-SPEC-000::8]

If pop-outs are supported, they shall remain subordinate to the authoritative backend session and shall rejoin the primary shell cleanly if closed or disconnected.

## 9. Human Review Focus [SEC:UDQ-UI-SPEC-000::9]

A human pass should verify that shell/navigation behavior preserves operator continuity, does not hide authority boundaries, and does not make review/history behavior ambiguous with live operation.
