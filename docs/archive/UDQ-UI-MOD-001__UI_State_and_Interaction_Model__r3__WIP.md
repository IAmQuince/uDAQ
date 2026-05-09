---
document_id: UDQ-UI-MOD-001
title: UI State and Interaction Model
revision: r3
status: WIP
document_class: ui_interaction_model
owner: UniversalDAQ
depends_on:
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-SPEC-004
  - UDQ-UI-SPEC-006
supersedes:
  - UDQ-UI-MOD-001__UI_State_and_Interaction_Model__r2__WIP.md
---

# UI State and Interaction Model [SEC:UDQ-UI-MOD-001::0]

The current bounded package explicitly separates runtime acquisition/evaluation cadence from UI refresh cadence and requires the UI model to consume summarized state rather than perform device or dependency-heavy work directly.

## Revision History [SEC:UDQ-UI-MOD-001::0.1]
- r3: Docs-only UI refinement pass. Added explicit Control workspace interaction states, draft/deployed/simulation transitions, evidence-pane linkage, and refined graph/live/review transitions.
- r2: Reconciliation pass clarifying workspace/session/machine-state boundaries and honest restore behavior.
- r1: Machine-readable normalization pass and content polish.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-UI-MOD-001::1]

This document defines how the UniversalDAQ UI behaves over time and in response to platform state, backend state, user actions, device conditions, data-quality conditions, remote participation, and recovery events.

It is not a page-layout specification. It is the governing interaction model for the UI.

## 2. Scope [SEC:UDQ-UI-MOD-001::2]

This model governs:
- shell lifecycle
- backend connectivity presentation
- workspace interaction states
- graph/live/review transitions
- control-authoring lifecycle states
- validation, simulation, apply, and rollback interaction
- evidence and audit linkage
- restore and reconnect behavior

## 2A. Semantic Closure and Anti-Conflation Rule [SEC:UDQ-UI-MOD-001::2A]

The UI shall not conflate:
- restored UI posture with restored machine truth
- draft intent with deployed behavior
- requested action with observed effect
- live graphing with historical review
- control-authoring validation with runtime proof
- remote capability with local capability

## 3. Core Interaction Principles [SEC:UDQ-UI-MOD-001::3]

### 3.1 Backend Truth Principle [SEC:UDQ-UI-MOD-001::3.1]
The backend remains authoritative for execution truth and command admission.

### 3.2 Honest State Principle [SEC:UDQ-UI-MOD-001::3.2]
The UI shall present current state honestly, including uncertainty and degraded status.

### 3.3 Mode-Dependent Editability Principle [SEC:UDQ-UI-MOD-001::3.3]
What the user can edit shall depend on workspace, object class, authority, and validation state.

### 3.4 Explainability Principle [SEC:UDQ-UI-MOD-001::3.4]
Interaction shall preserve the ability to answer why behavior occurred or did not occur.

### 3.5 Safe Recovery Principle [SEC:UDQ-UI-MOD-001::3.5]
Reconnect, restore, and replay behavior shall re-establish operator continuity without falsifying truth.

### 3.6 Preserve Successful Engineering Workflow Principle [SEC:UDQ-UI-MOD-001::3.6]
The UI shall preserve dense, efficient engineering flow while staying legible.

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

## 5. Application Shell States [SEC:UDQ-UI-MOD-001::5]

### 5.1 Launching [SEC:UDQ-UI-MOD-001::5.1]
The shell is assembling layout, preferences, and service endpoints. No restored posture shall be presented as live truth yet.

### 5.2 Restoring Session [SEC:UDQ-UI-MOD-001::5.2]
The shell may restore layout, selected workspace, graph preferences, and open inspectors. Restored edit surfaces shall be marked as restored UI posture until reconciled.

### 5.3 Ready [SEC:UDQ-UI-MOD-001::5.3]
The shell has enough information to present stable workspace identity and live or known-degraded backend posture.

### 5.4 Degraded Shell [SEC:UDQ-UI-MOD-001::5.4]
The shell is up, but one or more supporting services are unavailable or stale.

### 5.5 Closing [SEC:UDQ-UI-MOD-001::5.5]
The shell is persisting allowed local state, draining pending review artifacts, and making safe closure visible.

## 6. Backend Connectivity States [SEC:UDQ-UI-MOD-001::6]

### 6.1 Backend Unavailable [SEC:UDQ-UI-MOD-001::6.1]
The UI may still present local drafts, profiles, and historical review, but shall not imply live control.

### 6.2 Connecting [SEC:UDQ-UI-MOD-001::6.2]
The UI is waiting for authoritative runtime state.

### 6.3 Synchronized / Authoritative Live State [SEC:UDQ-UI-MOD-001::6.3]
The UI has current authoritative runtime information.

### 6.4 Backend Degraded [SEC:UDQ-UI-MOD-001::6.4]
The UI remains connected but one or more data or service paths are degraded.

### 6.5 Backend Lost After Prior Synchronization [SEC:UDQ-UI-MOD-001::6.5]
The UI retains last-known information but shall mark it as last-known rather than current.

## 7. Workspace Interaction States [SEC:UDQ-UI-MOD-001::7]

### 7.1 View-Only State [SEC:UDQ-UI-MOD-001::7.1]
The current surface is visible but not editable due to role, state, or policy.

### 7.2 Live Supervisory State [SEC:UDQ-UI-MOD-001::7.2]
The user is watching and possibly issuing bounded actions in Run.

### 7.3 Draft Editing State [SEC:UDQ-UI-MOD-001::7.3]
The user is modifying authored assets that are not yet deployed.

### 7.4 Validation State [SEC:UDQ-UI-MOD-001::7.4]
The system is checking references, units, dependencies, priorities, protections, or other authoring constraints.

### 7.5 Pending Apply State [SEC:UDQ-UI-MOD-001::7.5]
A draft is queued for apply/deploy or awaiting confirmation.

### 7.6 Active Runtime Execution State [SEC:UDQ-UI-MOD-001::7.6]
A rule, sequence, or bounded supervisory action is active in runtime, and the UI is presenting current runtime evidence.

### 7.7 Historical Review State [SEC:UDQ-UI-MOD-001::7.7]
The user is exploring history and evidence, not following live runtime.

### 7.8 Simulation State [SEC:UDQ-UI-MOD-001::7.8]
The user is running a non-live simulation, replay, or authoring-time test. All simulated values and outcomes shall be marked as such.

### 7.9 Audit Comparison State [SEC:UDQ-UI-MOD-001::7.9]
The user is comparing draft versus deployed or one revision versus another.

## 8. Control Authoring Lifecycle State Model [SEC:UDQ-UI-MOD-001::8]

### 8.1 Clean Draft [SEC:UDQ-UI-MOD-001::8.1]
An authored asset exists with no unsaved local changes.

### 8.2 Dirty Draft [SEC:UDQ-UI-MOD-001::8.2]
The user has modified a control asset locally.

### 8.3 Validation Warning [SEC:UDQ-UI-MOD-001::8.3]
The draft is syntactically acceptable but has warnings requiring user judgment.

### 8.4 Validation Error [SEC:UDQ-UI-MOD-001::8.4]
The draft cannot be applied because required validation has failed.

### 8.5 Simulation Ready [SEC:UDQ-UI-MOD-001::8.5]
The draft is coherent enough to simulate or replay.

### 8.6 Apply Ready [SEC:UDQ-UI-MOD-001::8.6]
The draft has passed required checks and may be intentionally applied.

### 8.7 Deployed [SEC:UDQ-UI-MOD-001::8.7]
The authored asset revision is the deployed runtime target.

### 8.8 Superseded / Rolled Back [SEC:UDQ-UI-MOD-001::8.8]
The previously deployed revision has been replaced or rolled back.

## 9. Data Representation and Quality State Model [SEC:UDQ-UI-MOD-001::9]

### 9.1 Good / Live [SEC:UDQ-UI-MOD-001::9.1]
Current and trustworthy.

### 9.2 Stale [SEC:UDQ-UI-MOD-001::9.2]
Not current enough for ordinary live interpretation.

### 9.3 Invalid [SEC:UDQ-UI-MOD-001::9.3]
Known invalid or failed to validate.

### 9.4 Disconnected / Unavailable [SEC:UDQ-UI-MOD-001::9.4]
The value or path is unavailable.

### 9.5 Simulated / Test [SEC:UDQ-UI-MOD-001::9.5]
Produced by test, replay, or simulation.

### 9.6 Derived [SEC:UDQ-UI-MOD-001::9.6]
Produced from one or more upstream values and therefore dependency-sensitive.

### 9.7 Historical [SEC:UDQ-UI-MOD-001::9.7]
Retrieved from stored history rather than current runtime.

### 9.8 Pending Command-Influenced State [SEC:UDQ-UI-MOD-001::9.8]
Potentially changing because a related action has been requested but not yet observed.

## 10. Trend and Visualization State Model [SEC:UDQ-UI-MOD-001::10]

### 10.1 Live Sliding Window [SEC:UDQ-UI-MOD-001::10.1]
The graph follows live runtime within a configured time horizon.

### 10.2 Whole Session / Whole History View [SEC:UDQ-UI-MOD-001::10.2]
The graph is viewing the full requested session or historical range.

### 10.3 Explore / Detached Review [SEC:UDQ-UI-MOD-001::10.3]
The user is freely panning, zooming, selecting ranges, or otherwise detached from automatic live follow.

### 10.4 Return-to-Live [SEC:UDQ-UI-MOD-001::10.4]
A deliberate user action returns the graph to live follow and re-establishes the active live time horizon.

### 10.5 Mixed Trust Visualization [SEC:UDQ-UI-MOD-001::10.5]
The graph is showing a combination of live, historical, simulated, or stale material; the UI shall mark those distinctions.

## 11. Editability Doctrine by Domain [SEC:UDQ-UI-MOD-001::11]

### 11.1 Devices / Protocols [SEC:UDQ-UI-MOD-001::11.1]
Editable in System when policy and capability allow.

### 11.2 Variables [SEC:UDQ-UI-MOD-001::11.2]
Editable in Control draft state; read-only while comparing or reviewing deployed evidence.

### 11.3 Logic / Protections / Modes [SEC:UDQ-UI-MOD-001::11.3]
Editable in Control draft state; must show validation and deployment posture.

### 11.4 Actions / Bindings [SEC:UDQ-UI-MOD-001::11.4]
Editable in Control draft state; requested-versus-observed evidence remains visible in runtime.

### 11.5 Sequences [SEC:UDQ-UI-MOD-001::11.5]
Editable in Control draft state, with runtime step state visible but clearly distinguished from draft editing.

### 11.6 Profiles / Session Preferences [SEC:UDQ-UI-MOD-001::11.6]
Editable as local or governed configuration according to policy.

## 12. Command Lifecycle Model [SEC:UDQ-UI-MOD-001::12]

### 12.1 User Intent Capture [SEC:UDQ-UI-MOD-001::12.1]
The user expresses intent through a bounded command surface.

### 12.2 Local Pre-Check [SEC:UDQ-UI-MOD-001::12.2]
The UI may warn about obvious missing prerequisites but shall not masquerade as the final arbiter.

### 12.3 Submission to Backend [SEC:UDQ-UI-MOD-001::12.3]
The command is submitted to the authoritative backend.

### 12.4 Pending State [SEC:UDQ-UI-MOD-001::12.4]
The command is awaiting admission or observed effect.

### 12.5 Backend Resolution [SEC:UDQ-UI-MOD-001::12.5]
The backend admits, rejects, supersedes, or otherwise resolves the request.

### 12.6 Result Visibility [SEC:UDQ-UI-MOD-001::12.6]
The UI shall surface both the resolution and any observed effect or missing confirmation.

### 12.7 Command Attribution [SEC:UDQ-UI-MOD-001::12.7]
The origin of the action shall remain visible.

## 13. Evidence Linkage Model [SEC:UDQ-UI-MOD-001::13]

### 13.1 Selection-to-Evidence [SEC:UDQ-UI-MOD-001::13.1]
Selecting a graph range, variable, rule, sequence step, or action shall update the relevant evidence surfaces when possible.

### 13.2 Evidence-to-Authoring [SEC:UDQ-UI-MOD-001::13.2]
From a runtime event or audit record, the user shall be able to inspect the authored object that produced it.

### 13.3 Evidence-to-Review [SEC:UDQ-UI-MOD-001::13.3]
The user shall be able to move from live observation into review without losing the causal thread.

## 14. Startup and Restore Behavior [SEC:UDQ-UI-MOD-001::14]

### 14.1 What Shall Restore [SEC:UDQ-UI-MOD-001::14.1]
Layout, graph selections, open tabs, inspector posture, and draft editing context may restore.

### 14.2 What Shall Not Be Assumed Restored as Truth [SEC:UDQ-UI-MOD-001::14.2]
Current values, active device identity, output effect, and live authority shall not be assumed from local restore alone.

### 14.3 Restore Reconciliation [SEC:UDQ-UI-MOD-001::14.3]
The UI shall reconcile restored posture against current backend truth before removing restored-state cues.

### 14.4 Autosave / Dirty-State Model [SEC:UDQ-UI-MOD-001::14.4]
Autosave may preserve drafts and layout, but shall preserve the draft-versus-deployed distinction.

## 15. Disconnect and Reconnect Behavior [SEC:UDQ-UI-MOD-001::15]

### 15.1 Device Disconnect [SEC:UDQ-UI-MOD-001::15.1]
Affected values and dependent assets shall visibly degrade.

### 15.2 Backend Disconnect [SEC:UDQ-UI-MOD-001::15.2]
Live command affordances shall degrade or disable according to policy, while drafts and review may remain available.

### 15.3 Reconnect [SEC:UDQ-UI-MOD-001::15.3]
Upon reconnect, the UI shall re-establish truth and clearly show what was local draft continuity versus freshly reconciled runtime state.

## 16. Summary [SEC:UDQ-UI-MOD-001::16]

The UniversalDAQ UI interaction model is built around honest state boundaries: live versus review, draft versus deployed, requested versus observed, and local continuity versus machine truth. It explicitly includes validation, simulation, apply, rollback, and evidence linkage so that the Control workspace feels trustworthy and the graph/review surfaces remain causally connected to authored behavior.
