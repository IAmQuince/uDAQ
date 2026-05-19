---
document_id: UDQ-UI-MOD-001
title: UI State and Interaction Model
revision: r5
status: WIP
document_class: ui_interaction_model
owner: UniversalDAQ
depends_on:
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-SPEC-004
  - UDQ-UI-SPEC-006
supersedes:
  - UDQ-UI-MOD-001__UI_State_and_Interaction_Model__r3__WIP.md
---

# UI State and Interaction Model [SEC:UDQ-UI-MOD-001::0]

The current bounded package explicitly separates runtime acquisition/evaluation cadence from UI refresh cadence and requires the UI model to consume summarized state rather than perform device or dependency-heavy work directly.

## Revision History [SEC:UDQ-UI-MOD-001::0.1]
- r5: 2026-03-30 documentation closeout. Added selected-device context, canonical device-I/O inventory ownership, graph-mode/PiP recovery state, and explicit applied/draft/unavailable authority semantics in the shell model.
- r4: Docs-only UI alignment pass. Renamed workspace interaction states around Operate, Logic Designer, Session Review, and System; added browser-lens and graph-setup interaction concepts; and refined live/historical/simulated review boundaries.
- r3: Docs-only UI refinement pass. Added explicit Control workspace interaction states, draft/deployed/simulation transitions, evidence-pane linkage, and refined graph/live/review transitions.
- r2: Reconciliation pass clarifying workspace/session/machine-state boundaries and honest restore behavior.

## 1. Purpose [SEC:UDQ-UI-MOD-001::1]

This document defines how the UniversalDAQ UI behaves over time and in response to platform state, backend state, user actions, device conditions, data-quality conditions, replay/simulation conditions, and recovery events.

## 2. Scope [SEC:UDQ-UI-MOD-001::2]

This model governs:
- shell lifecycle
- backend connectivity presentation
- workspace interaction states
- graph/live/review transitions
- logic-designer lifecycle states
- validation, simulation, monitor-live, apply, and rollback interaction
- evidence and audit linkage
- restore and reconnect behavior

## 3. Core Interaction Principles [SEC:UDQ-UI-MOD-001::3]

The UI shall preserve:
- honest state
- explicit live versus historical distinction
- explicit draft versus deployed distinction
- explicit simulated versus observed distinction
- mode-dependent editability
- safe recovery without false continuity

## 4. State Model Overview [SEC:UDQ-UI-MOD-001::4]

The interaction model contains the following state domains:
- shell state
- backend connectivity state
- workspace interaction state
- authoring lifecycle state
- graph and review state
- data quality state
- command lifecycle state
- authority and ownership state
- browser lens and graph-setup state

## 5. Workspace Interaction States [SEC:UDQ-UI-MOD-001::5]

The principal workspace interaction states are:
- Operate live supervisory state
- Logic Designer draft editing state
- Logic Designer validation state
- Logic Designer simulation state
- Logic Designer monitor-live state
- Session Review historical state
- Audit comparison state
- System configuration/diagnostics state

## 6. Browser Lens State [SEC:UDQ-UI-MOD-001::6]

The shell shall make it explicit whether the user is currently browsing through:
- Hardware lens
- Raw lens
- Logical lens
- Derived lens
- Control lens
- Saved Set / Favorites lens

Lens changes shall not be mistaken for signal-identity changes. They alter browse and naming context, not the underlying stable signal identity.

## 7. Graph Setup State [SEC:UDQ-UI-MOD-001::7]

The graphing surface shall maintain explicit state for:
- active graph setup
- active time horizon
- active trace selection/focus
- historical/live/simulated posture
- unsaved graph-style changes where applicable

## 8. Data Representation and Quality States [SEC:UDQ-UI-MOD-001::8]

Data quality states shall include at minimum:
- fresh / live
- stale
- invalid
- disconnected / unavailable
- simulated / test
- derived / dependency-sensitive
- historical
- pending command-influenced

## 9. Historical Review and Restore Rule [SEC:UDQ-UI-MOD-001::9]

Historical review, replay, and restored convenience state shall remain visibly distinct from authoritative current live truth. The UI shall therefore label historical previews, restored context, and simulated values explicitly.

## 10. Human Review Focus [SEC:UDQ-UI-MOD-001::10]

A reviewer should quickly confirm that:
- workspace states reflect Operate, Logic Designer, Session Review, and System
- browser lens changes do not silently redefine stable signal identity
- graph setups and restored context remain distinct from current live truth
- simulation and monitor-live remain distinct from apply/deployed behavior

## 5A. Operator Shell Foundation State [SEC:UDQ-UI-MOD-001::5A]

The UI state model shall reserve explicit shell-facing models for:
- persistent top information bar state
- dock-layout preferences with right-side control-dock default
- user-demo posture and active demo-scenario selection
- trace presentation, legend preferences, and autosave preferences

These models are shell-facing pure state and shall not require direct widget instantiation.

## 2026-03-28 implementation addendum — interaction split
- The UI interaction model now distinguishes raw hardware navigation, internal signal navigation, and binding edits as separate operator intents.
- Mapping edits shall remain bounded to binding metadata such as direction, scale/offset, invert, enable/disable, and notes; transform authoring remains outside this surface.
- Structured events browsing is treated as filtered/searchable session state rather than a single undifferentiated text log.

## 2026-03-29 implementation addendum — shell policy versus runtime truth
- shell geometry, graph presentation, PiP placement, and splitter sizes are presentation state only and must not redefine runtime truth.
- draft mapping rows in the visible shell remain non-authoritative until controller-backed apply semantics exist.
- capability evidence shown in the UI shall distinguish generic baseline discovery from enhanced support-pack operation explicitly.


## 2026-03-30 documentation closeout addendum — selected-device and authority context
- The UI interaction model now reserves explicit state for **selected device context**. Selecting a device establishes a canonical device-I/O inventory context that System, Device Explorer, Signal Explorer filters, trace labels, and Logic-source browsers may reference without redefining identity.
- Graph presentation state shall expose `Primary`, `PiP`, and `Hidden` as explicit shell presentation modes. The presence or absence of PiP is presentation state only and must never imply a change in runtime truth.
- Authority-facing state shown in the shell shall use the vocabulary `Applied`, `Draft`, `Unavailable`, and `Unmapped`. `Applied` is backend-authoritative. `Draft` is shell-side proposal or simulated state. `Unavailable` means authoritative readback is not currently available. `Unmapped` means no current relationship is established.
