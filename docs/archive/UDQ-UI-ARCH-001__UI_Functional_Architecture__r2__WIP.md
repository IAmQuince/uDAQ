---
document_id: UDQ-UI-ARCH-001
title: UI Functional Architecture
revision: r2
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
  - UDQ-UI-ARCH-001__UI_Functional_Architecture__r1__WIP.md
---

# UI Functional Architecture [SEC:UDQ-UI-ARCH-001::0]

## Revision History [SEC:UDQ-UI-ARCH-001::0.1]
- r2: Docs-only UI refinement pass. Reorganized the architecture around Run, Control, Review, and System workspaces; formalized the evidence spine and optional inspector; and reframed the sequence surface as a supporting control-authoring feature rather than the main organizing metaphor.
- r1: Initial functional architecture and subsystem decomposition pass.

## 1. Purpose [SEC:UDQ-UI-ARCH-001::1]

This document defines the functional architecture of the UniversalDAQ UI. It governs how the UI is decomposed into major workspaces, shell regions, cross-cutting services, and operator-facing behavior boundaries.

It is intentionally a functional architecture document rather than a widget map. Its purpose is to define what the UI must do and how major surfaces relate.

## 2. Scope [SEC:UDQ-UI-ARCH-001::2]

This architecture covers:
- the primary application shell
- workspace decomposition
- control-authoring workspace architecture
- graphing and evidence review architecture
- device, diagnostics, and configuration surfaces
- remote surface alignment
- cross-cutting UI services such as validation, audit, search, filtering, and persistence

## 3. Architectural Intent [SEC:UDQ-UI-ARCH-001::3]

The UI architecture shall support a universal engineering workflow in which the user can move cleanly between:
- live supervision
- control authoring
- evidence review
- system configuration and service

The architecture shall avoid:
- device-specific shell assumptions
- page proliferation without clear purpose
- mixing authoring and runtime evidence in one ambiguous surface
- hiding trust mechanisms such as validation, simulation, or audit behind secondary tools

## 4. Top-Level Functional Decomposition [SEC:UDQ-UI-ARCH-001::4]

The top-level functional decomposition is:

1. **Shell and layout framework**
2. **Run workspace**
3. **Control workspace**
4. **Review workspace**
5. **System workspace**
6. **Cross-cutting interaction and evidence services**
7. **Remote surfaces**

These are architectural domains, not necessarily separate processes or packages.

## 5. UI Shell and Window Framework [SEC:UDQ-UI-ARCH-001::5]

### 5.1 Role [SEC:UDQ-UI-ARCH-001::5.1]
The shell hosts the graph-centered work area, workspace navigation, dockable tooling, evidence pane, and optional inspector.

### 5.2 Responsibilities [SEC:UDQ-UI-ARCH-001::5.2]
The shell shall provide:
- persistent top-level workspace navigation
- a main work area centered on graphing or the current task surface
- a primary dock rail that may live on the left or right
- a lower evidence pane for events, alarms, diagnostics, command outcomes, notes, and similar review artifacts
- an optional inspector/detail pane for the selected object
- layout persistence and named layout presets

### 5.3 Architectural Rule [SEC:UDQ-UI-ARCH-001::5.3]
The shell shall preserve context while making live/review/authoring boundaries explicit. It shall not silently collapse those boundaries merely because the same frame or graph widget is reused.

## 6. Run Workspace [SEC:UDQ-UI-ARCH-001::6]

### 6.1 Role [SEC:UDQ-UI-ARCH-001::6.1]
Run is the live supervision workspace.

### 6.2 Responsibilities [SEC:UDQ-UI-ARCH-001::6.2]
Run shall provide:
- live graphing
- key values and status
- current protections/interlocks summary
- current sequence state if applicable
- bounded command-capable controls where authorized
- quick access to evidence overlays and return to live

### 6.3 Required Behavior [SEC:UDQ-UI-ARCH-001::6.3]
Run shall remain optimized for comprehension and bounded action rather than for deep authoring.

## 7. Control Workspace [SEC:UDQ-UI-ARCH-001::7]

### 7.1 Role [SEC:UDQ-UI-ARCH-001::7.1]
Control is the main authoring and trust-building workspace for control behavior.

### 7.2 Responsibilities [SEC:UDQ-UI-ARCH-001::7.2]
Control shall host the following governed subtabs or equivalent sub-surfaces:
- Overview
- Variables
- Logic
- Sequence
- Interlocks / Protections
- Actions / Bindings
- Modes / States
- Test / Simulation
- Audit / History

### 7.3 Architectural Rule [SEC:UDQ-UI-ARCH-001::7.3]
Control shall not be reduced to a single rules page or a single sequencer page. It is the composite workspace that turns authored intent into validated, simulated, deployable, and reviewable control assets.

### 7.4 Representation Rule [SEC:UDQ-UI-ARCH-001::7.4]
The primary representation inside Control shall be structured-first: inventory tables, cards, inspectors, dependency views, validation summaries, and runtime evidence. Diagram views may exist, but they shall be secondary to deterministic structured authoring.

### 7.5 Sequence Convenience Requirement [SEC:UDQ-UI-ARCH-001::7.5]
The Sequence subtab remains a required supporting feature because users sometimes need a convenient procedural surface for timed steps, ramps, setpoint moves, output profiles, and internal or virtual variable changes without invoking a broader state machine. The architecture shall preserve that convenience while keeping sequence authoring separate from the rest of the control-authoring model.

## 8. Review Workspace [SEC:UDQ-UI-ARCH-001::8]

### 8.1 Role [SEC:UDQ-UI-ARCH-001::8.1]
Review is the historical, evidence, and forensic workspace.

### 8.2 Responsibilities [SEC:UDQ-UI-ARCH-001::8.2]
Review shall provide:
- historian access
- graph exploration
- event, alarm, and command timelines
- notes and annotations
- exported evidence artifacts
- correlation between graph ranges and the lower evidence pane

### 8.3 Architectural Position [SEC:UDQ-UI-ARCH-001::8.3]
Review is distinct from Run even when it reuses the same graphing substrate. Review prioritizes range exploration, comparison, and evidence gathering rather than live follow.

## 9. System Workspace [SEC:UDQ-UI-ARCH-001::9]

### 9.1 Role [SEC:UDQ-UI-ARCH-001::9.1]
System is the configuration, diagnostics, and service workspace.

### 9.2 Responsibilities [SEC:UDQ-UI-ARCH-001::9.2]
System shall provide:
- device discovery and onboarding
- capability and identity review
- bindings and point maps where appropriate
- diagnostics and dependency visibility
- profiles, settings, and persistence controls
- service/state and support-pack visibility

### 9.3 Architectural Rule [SEC:UDQ-UI-ARCH-001::9.3]
System may expose advanced or protocol-specific detail without forcing ordinary runtime users through those details.

## 10. Lower Evidence Pane [SEC:UDQ-UI-ARCH-001::10]

### 10.1 Role [SEC:UDQ-UI-ARCH-001::10.1]
The lower pane is the evidence spine shared across workspaces.

### 10.2 Responsibilities [SEC:UDQ-UI-ARCH-001::10.2]
It shall host:
- events
- alarms
- command outcomes
- diagnostics summaries
- notes and annotations
- validation results
- simulation outcomes
- selected-range evidence tables

### 10.3 Architectural Rule [SEC:UDQ-UI-ARCH-001::10.3]
The lower pane shall help answer “what happened here?” without forcing context switches into isolated log-only screens.

## 11. Optional Inspector / Detail Surface [SEC:UDQ-UI-ARCH-001::11]

### 11.1 Role [SEC:UDQ-UI-ARCH-001::11.1]
The inspector provides focused detail for the currently selected object.

### 11.2 Responsibilities [SEC:UDQ-UI-ARCH-001::11.2]
The inspector may show:
- metadata
- dependencies
- usage references
- validation issues
- last runtime value
- last action or last fired evidence
- related notes or audit history

### 11.3 Architectural Rule [SEC:UDQ-UI-ARCH-001::11.3]
The inspector is a supporting surface. It shall reduce clutter in primary views, not become a hidden primary control surface.

## 12. Graphing and Trend Review Architecture [SEC:UDQ-UI-ARCH-001::12]

### 12.1 Role [SEC:UDQ-UI-ARCH-001::12.1]
Graphing is the central evidence surface shared across Run and Review, and partially reused inside Control for explainability and simulation review.

### 12.2 Responsibilities [SEC:UDQ-UI-ARCH-001::12.2]
The graphing architecture shall support:
- live follow and sliding window
- whole-history review
- free explore mode
- return to live
- overlays for events, commands, rule firings, sequence transitions, and notes
- user-selected trace groups and linked range-to-evidence review

### 12.3 Preservation Requirement [SEC:UDQ-UI-ARCH-001::12.3]
The graph shall preserve the operator value of the earlier Genesys line while being generalized to multi-device, multi-signal, and evidence-rich UniversalDAQ use cases.

## 13. Cross-Cutting Interaction Services [SEC:UDQ-UI-ARCH-001::13]

Cross-cutting services shall include at least:
- search and filter
- object dependency inspection
- validation
- simulation/replay launch points
- draft-versus-deployed comparison
- audit/history visibility
- export and evidence capture
- layout persistence
- attribution and authority visibility

These are shared concerns and shall not be reimplemented ad hoc inside each workspace.

## 14. Remote Observation and Remote Supervision Surfaces [SEC:UDQ-UI-ARCH-001::14]

### 14.1 Role [SEC:UDQ-UI-ARCH-001::14.1]
Remote surfaces expose bounded subsets of Run, Review, and in some deployments selected Control or System affordances.

### 14.2 Responsibilities [SEC:UDQ-UI-ARCH-001::14.2]
Remote surfaces shall:
- preserve truth about latency and connectivity
- preserve attribution
- expose only policy-permitted actions
- avoid implying local parity where it does not exist

### 14.3 Architectural Rule [SEC:UDQ-UI-ARCH-001::14.3]
Remote is not a separate truth model. It is a policy-bounded surface on the same governed state.

## 15. Workspace Relationships [SEC:UDQ-UI-ARCH-001::15]

The major workspace relationships are:

- Run links to Control when the user wants to inspect why a value, rule, or sequence behaved as observed.
- Control links to Review when the user needs historical evidence or replay for authoring confidence.
- Review links back to Run through explicit return-to-live behavior.
- System feeds Control through device, point, and capability discovery.
- The lower pane and inspector provide common continuity across all of them.

## 16. Recommended Default Workspace Posture [SEC:UDQ-UI-ARCH-001::16]

The recommended default posture is:
- Run as the landing workspace for ordinary operation
- Control as the main authoring workspace
- Review as the evidence and forensic workspace
- System as the configuration and diagnostics workspace
- top bar for status and quick actions
- dock rail on user-chosen left or right side
- lower evidence pane visible by default in compact form

## 17. What This Architecture Explicitly Preserves from Genesys [SEC:UDQ-UI-ARCH-001::17]

This architecture preserves:
- graph dominance
- dockable engineering panels
- sliding-window live behavior plus free explore and return to live
- convenient procedural sequencing where useful
- dense professional ergonomics

It does not preserve:
- page taxonomy tied to one tool
- fixed device-specific control pages as architectural primitives
- the assumption that sequence editing is the main control-authoring paradigm

## 18. Architectural Non-Goals for This Document [SEC:UDQ-UI-ARCH-001::18]

This document does not define:
- exact widget placement
- toolkit-specific docking APIs
- renderer or plotting library choices
- backend execution semantics
- control language grammar details

Those belong in more detailed specs or implementation slices.

## 19. Summary [SEC:UDQ-UI-ARCH-001::19]

The UniversalDAQ UI architecture is a graph-centered shell with four major workspaces: Run, Control, Review, and System. A shared lower evidence pane and optional inspector create continuity between live supervision, control authoring, historical review, and service/diagnostics. The architecture preserves useful engineering ergonomics from earlier tools while explicitly broadening the UI into a trustworthy, workspace-based control-authoring environment.
