---
document_id: UDQ-UI-MOD-001
title: UI State and Interaction Model
revision: r1
status: WIP
document_class: ui_state_model
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-LOG-001
  - UDQ-ARCH-NAR-001
  - UDQ-ARCH-NAR-002
  - UDQ-REQ-MAT-001
  - UDQ-QUAL-DEF-001
  - UDQ-UI-INV-001
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
supersedes:
  - UDQ-UI-MOD-001__UI_State_and_Interaction_Model__r0__WIP.md
---

# UI State and Interaction Model [SEC:UDQ-UI-MOD-001::0]

## Revision History [SEC:UDQ-UI-MOD-001::0.1]
- r1: Machine-readable normalization pass, unique section anchors, metadata cleanup, and content polish against the current governed corpus.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-UI-MOD-001::1]
This document defines how the UniversalDAQ user interface behaves over time and in response to platform state, backend state, user actions, device conditions, data-quality conditions, remote participation, and recovery events.

This is not a page-layout specification. It is the governing interaction model for the UI. It defines the operational states the UI may inhabit, what the operator may or may not do in each state, how the UI shall present truth and uncertainty, how command requests move from human intent to backend arbitration, and how session persistence shall and shall not behave.

## 2. Scope [SEC:UDQ-UI-MOD-001::2]
This document applies to:
- local operator-facing UI instances,
- engineering/service UI instances,
- remote observation and remote supervision clients,
- all workspaces defined in the UI Functional Architecture,
- all user interactions involving devices, signals, derived signals, outputs, rules, sequences, historian, events, diagnostics, and profiles.

This document does not yet define exact widget sets, exact visual styling, exact role-based security implementation, or protocol-specific edit forms. Those belong to later subsystem and workspace specifications.

## 3. Core Interaction Principles [SEC:UDQ-UI-MOD-001::3]

## 3.1 Backend Truth Principle [SEC:UDQ-UI-MOD-001::3.1]
The UI shall not be treated as the source of truth for system state, output state, device state, historian state, or authoritative command resolution. The backend remains authoritative.

## 3.2 Honest State Principle [SEC:UDQ-UI-MOD-001::3.2]
The UI shall represent live, historical, stale, invalid, disconnected, simulated, derived, pending, faulted, blocked, and restored state distinctly enough that an informed user cannot reasonably confuse them.

## 3.3 Mode-Dependent Editability Principle [SEC:UDQ-UI-MOD-001::3.3]
What may be edited, commanded, acknowledged, or restored shall depend on current system mode, workspace mode, backend state, and authority context. UI editability shall never imply backend acceptance.

## 3.4 Explainability Principle [SEC:UDQ-UI-MOD-001::3.4]
Whenever the UI blocks an action, marks data untrusted, disables a command, or shows that a requested output is not taking effect, the UI shall expose an understandable reason path.

## 3.5 Safe Recovery Principle [SEC:UDQ-UI-MOD-001::3.5]
After startup, reconnect, crash recovery, profile restore, or communication restoration, the UI shall recover operator continuity without silently asserting stale assumptions as current machine truth.

## 3.6 Preserve Successful Engineering Workflow Principle [SEC:UDQ-UI-MOD-001::3.6]
The UI state model shall preserve the successful Genesys engineering posture: graph-dominant operation, dockable dense control workflows, rapid transition between live operation and review, and visibility into logs/diagnostics, while generalizing those behaviors for UniversalDAQ.

## 4. State Model Overview [SEC:UDQ-UI-MOD-001::4]
The UniversalDAQ UI shall be understood in terms of multiple simultaneous state domains rather than a single flat application state.

## 4.1 State Domains [SEC:UDQ-UI-MOD-001::4.1]
The UI interaction model shall distinguish at least the following state domains:
- **Application shell state** — whether the UI process is launching, restoring, ready, degraded, or closing.
- **Backend connectivity state** — whether authoritative backend contact is unavailable, connecting, synchronized, degraded, or lost.
- **Workspace state** — whether a workspace is live, historical, editing, validating, running, blocked, or read-only.
- **Data quality state** — whether displayed values are good, stale, invalid, disconnected, simulated, estimated, or historical.
- **Authority state** — whether a commandable point is locally requested, remotely requested, sequence-owned, rule-owned, manual-owned, safe-state-owned, blocked, or backend-resolved to another owner.
- **Session persistence state** — whether UI layout/profile/session state is default, restored, modified, dirty, saved, conflicted, or partially restorable.

These state domains may coexist. For example, the application shell may be ready while the backend is degraded, one workspace is read-only, another is in local draft edit mode, and specific signals are stale.

## 5. Application Shell States [SEC:UDQ-UI-MOD-001::5]

## 5.1 Launching [SEC:UDQ-UI-MOD-001::5.1]
During launch, the UI may initialize its shell, layout framework, persisted settings, local caches, and backend connection processes.

During this state the UI shall:
- make clear that startup is in progress,
- avoid presenting cached values as authoritative live values,
- avoid enabling direct command surfaces that imply resolved authority,
- allow access only to appropriate non-authoritative local shell actions where sensible.

## 5.2 Restoring Session [SEC:UDQ-UI-MOD-001::5.2]
A restoring-session state shall exist when the UI is applying persisted layout, reopening docks/workspaces, restoring user preferences, and reconstructing prior local working context.

During this state the UI shall:
- distinguish restored local context from live backend confirmation,
- restore window placement, dock positions, selected workspaces, trend-view preferences, and other local UI preferences,
- avoid automatically reissuing previously pending or manual control commands,
- avoid implying that restored controls represent current machine state until backend synchronization completes.

## 5.3 Ready [SEC:UDQ-UI-MOD-001::5.3]
The ready state exists when the UI shell is operational and able to support normal workspace interaction.

Ready does not necessarily mean fully connected to all devices or backend services. The UI shall therefore expose ready state separately from backend-health state.

## 5.4 Degraded Shell [SEC:UDQ-UI-MOD-001::5.4]
The degraded-shell state exists when the UI process remains usable but one or more cross-cutting UI services are impaired, such as logging surface impairment, historian review impairment, workspace rendering impairment, or partial restore failure.

The UI shall continue operating where safe and shall expose what parts remain trustworthy.

## 5.5 Closing [SEC:UDQ-UI-MOD-001::5.5]
During shutdown the UI shall:
- indicate that orderly closure is occurring,
- preserve local state where appropriate,
- avoid presenting closure-time transient values as stable state,
- not silently discard important unsaved draft changes without warning,
- not imply that UI closure itself performs device-safe-state action unless such action is actually backend-supported and declared.

## 6. Backend Connectivity States [SEC:UDQ-UI-MOD-001::6]

## 6.1 Backend Unavailable [SEC:UDQ-UI-MOD-001::6.1]
This state exists when no authoritative backend is reachable.

The UI shall in this state:
- present historical and local configuration material as non-authoritative,
- disable or strongly constrain live command actions,
- clearly label unavailable live control and unavailable live truth,
- permit access to local drafts, review artifacts, and prior evidence where safe.

## 6.2 Connecting [SEC:UDQ-UI-MOD-001::6.2]
The UI may display backend connection progress and partial service discovery.

During this phase the UI shall not treat partial subscription or incomplete backend metadata as complete readiness.

## 6.3 Synchronized / Authoritative Live State [SEC:UDQ-UI-MOD-001::6.3]
This state exists when the UI has synchronized enough backend information to present authoritative live values, live ownership state, and command resolution state for the supported surfaces.

## 6.4 Backend Degraded [SEC:UDQ-UI-MOD-001::6.4]
This state exists when backend contact remains present but one or more essential capabilities are impaired, such as delayed publication, historian lag, partial device status gaps, command-ack lag, or incomplete dependency visibility.

The UI shall distinguish degraded from absent. It shall expose which capabilities remain usable and which are untrustworthy or reduced.

## 6.5 Backend Lost After Prior Synchronization [SEC:UDQ-UI-MOD-001::6.5]
If backend contact is lost after prior sync, the UI shall:
- preserve last-known state as explicitly last-known,
- visibly age the trustworthiness of displayed data,
- prevent silent continuation of authority assumptions,
- preserve local draft edits where possible,
- not silently replay queued commands unless explicitly designed and governed later.

## 7. Workspace Interaction States [SEC:UDQ-UI-MOD-001::7]
Each workspace may have additional states layered on top of the shell/backend states.

## 7.1 View-Only State [SEC:UDQ-UI-MOD-001::7.1]
A workspace is view-only when it can present information but not allow edits or commanding. Causes may include read-only role, backend unavailability, selected historical context, policy lockout, or active execution that forbids edits.

## 7.2 Live Supervisory State [SEC:UDQ-UI-MOD-001::7.2]
A workspace is in live supervisory state when it is bound to authoritative live backend data and permits non-destructive runtime supervision actions appropriate to the workspace.

## 7.3 Draft Editing State [SEC:UDQ-UI-MOD-001::7.3]
A workspace is in draft editing state when the user is preparing changes to configuration, rules, sequences, mappings, profiles, or derived signals that are not yet validated or activated.

In this state the UI shall preserve the distinction between draft objects and active deployed objects.

## 7.4 Validation State [SEC:UDQ-UI-MOD-001::7.4]
A workspace enters validation state when proposed changes are being checked for syntax, references, capabilities, dependency conflicts, ownership conflicts, quality implications, or deployment policy violations.

## 7.5 Pending Apply State [SEC:UDQ-UI-MOD-001::7.5]
A workspace is in pending apply state when changes have passed local checks and are awaiting backend acceptance, deployment confirmation, or activation.

## 7.6 Active Runtime Execution State [SEC:UDQ-UI-MOD-001::7.6]
Certain workspaces such as sequences, outputs, and rules may have runtime execution states in which active logic or procedures are running. The UI shall then distinguish edit paths from observation/control paths.

## 7.7 Historical Review State [SEC:UDQ-UI-MOD-001::7.7]
A workspace is in historical review state when it is intentionally showing past data or replay data rather than the current live view.

The UI shall make it impossible to confuse review-state visuals with current live-state visuals.

## 8. Data Representation and Quality State Model [SEC:UDQ-UI-MOD-001::8]

## 8.1 Good / Live [SEC:UDQ-UI-MOD-001::8.1]
Good/live data is current authoritative data from the backend/device pipeline and may be used for normal supervisory understanding.

## 8.2 Stale [SEC:UDQ-UI-MOD-001::8.2]
Stale data is data whose value may remain visible but whose age exceeds its freshness contract. The UI shall show stale state prominently enough to affect operator trust.

## 8.3 Invalid [SEC:UDQ-UI-MOD-001::8.3]
Invalid data is data that exists but is not currently trustworthy as a numeric or logical basis for normal use. The UI shall not present invalid values in a way that looks merely low or zero.

## 8.4 Disconnected / Unavailable [SEC:UDQ-UI-MOD-001::8.4]
This state exists when no current path to the source exists. The UI shall differentiate missing transport from invalid decoded content.

## 8.5 Simulated / Test [SEC:UDQ-UI-MOD-001::8.5]
Simulated or injected test data shall be unmistakable. It shall never visually masquerade as ordinary live plant data.

## 8.6 Derived [SEC:UDQ-UI-MOD-001::8.6]
Derived values shall be identifiable as derived, not raw acquisition values. Where practical the UI should expose dependency and freshness implications.

## 8.7 Historical [SEC:UDQ-UI-MOD-001::8.7]
Historical values shall be visibly historical when presented outside clearly historical review contexts, especially in inspectors and comparison views.

## 8.8 Pending Command-Influenced State [SEC:UDQ-UI-MOD-001::8.8]
When a displayed value may soon change because of a pending command request, the UI may indicate a pending influence state, but shall not prematurely present the target condition as already achieved.

## 9. Trend and Visualization State Model [SEC:UDQ-UI-MOD-001::9]
The Genesys pattern of live graphing plus whole-session review shall be preserved and generalized.

## 9.1 Live Sliding Window [SEC:UDQ-UI-MOD-001::9.1]
The UI shall support a live sliding-window mode for runtime monitoring. In this state the visual focus is on recent behavior and ongoing response.

## 9.2 Whole Session / Whole History View [SEC:UDQ-UI-MOD-001::9.2]
The UI shall support a whole-session or broader-history view distinct from the sliding window. This mode shall not pretend to update with identical cadence or behavior as the live sliding window unless that is actually true.

## 9.3 Explore / Detached Review [SEC:UDQ-UI-MOD-001::9.3]
Users shall be able to pan, zoom, inspect, and temporarily detach from live-follow behavior.

## 9.4 Return-to-Live [SEC:UDQ-UI-MOD-001::9.4]
The UI shall provide an explicit path back to live-follow operation. Returning to live shall be a conscious mode transition, not a silent snap that causes user disorientation.

## 9.5 Mixed Trust Visualization [SEC:UDQ-UI-MOD-001::9.5]
When traces with different quality or freshness states coexist, the UI shall preserve their distinctions rather than flattening them into visually equivalent series.

## 10. Editability Doctrine by Domain [SEC:UDQ-UI-MOD-001::10]

## 10.1 Devices / Protocols [SEC:UDQ-UI-MOD-001::10.1]
Device definitions, protocol mappings, and point maps may be editable in draft form. Activation shall depend on validation and backend acceptance. Live communication state shall not be overwritten by a local draft.

## 10.2 Signals / Derived Signals [SEC:UDQ-UI-MOD-001::10.2]
Signal metadata may be editable subject to scope. Derived signal definitions shall support draft, validation, activation, and revision traceability.

## 10.3 Outputs / Commands [SEC:UDQ-UI-MOD-001::10.3]
Command surfaces shall be editable only where policy, mode, and authority allow. Editable target parameters shall be distinguished from current resolved output state.

## 10.4 Rules / Conditions / Actions [SEC:UDQ-UI-MOD-001::10.4]
Rule objects shall support dual editing modes in the future: structured visual builder and function-style DSL view. Both shall obey draft/validate/apply/activate transitions.

## 10.5 Sequences / Workflows [SEC:UDQ-UI-MOD-001::10.5]
Sequence definitions shall support draft editing separate from active execution. Editing an active sequence definition shall not silently rewrite the running instance unless an explicit governed mechanism exists.

## 10.6 Profiles / Session Preferences [SEC:UDQ-UI-MOD-001::10.6]
UI profiles and layout state shall support save/load/restore flows but shall remain distinct from backend runtime control configuration unless explicitly linked.

## 11. Command Lifecycle Model [SEC:UDQ-UI-MOD-001::11]

## 11.1 User Intent Capture [SEC:UDQ-UI-MOD-001::11.1]
A command begins as user intent in the UI. The UI shall capture sufficient context to form an explicit request rather than an ambiguous gesture.

## 11.2 Local Pre-Check [SEC:UDQ-UI-MOD-001::11.2]
Before submission, the UI may perform local pre-checks such as field validity, obvious range violations, missing dependencies, or missing selection context. These checks do not replace backend arbitration.

## 11.3 Submission to Backend [SEC:UDQ-UI-MOD-001::11.3]
Commands shall be submitted to the backend as requests. The UI shall not present submission as final acceptance.

## 11.4 Pending State [SEC:UDQ-UI-MOD-001::11.4]
After submission the UI shall show the command as pending where relevant, especially if resulting state change is not immediate.

## 11.5 Backend Resolution [SEC:UDQ-UI-MOD-001::11.5]
The backend may accept, reject, defer, clamp, redirect, block, or supersede the request according to system doctrine. The UI shall reflect this resolved outcome.

## 11.6 Result Visibility [SEC:UDQ-UI-MOD-001::11.6]
Where a command does not produce the requested final state, the UI shall show whether the cause was rejection, conflict, interlock, permissive failure, lost authority, device problem, or timeout/unknown result.

## 11.7 Command Attribution [SEC:UDQ-UI-MOD-001::11.7]
The UI shall preserve visibility into command origin where practical: local operator, remote supervisor, rule engine, sequence engine, safe-state logic, or other backend authority source.

## 12. Output Ownership and Authority Interaction [SEC:UDQ-UI-MOD-001::12]

## 12.1 Ownership Visibility [SEC:UDQ-UI-MOD-001::12.1]
For each commandable point, the UI shall expose who or what currently owns effective authority, or whether ownership is unresolved or blocked.

## 12.2 Requested vs Effective State [SEC:UDQ-UI-MOD-001::12.2]
The UI shall distinguish:
- requested state,
- resolved target state,
- effective reported output/device state,
- blocked or inhibited state.

## 12.3 Manual Interaction [SEC:UDQ-UI-MOD-001::12.3]
When manual interaction is allowed, the UI shall show manual control explicitly. Manual entry shall not be visually indistinguishable from automatic rule-driven or sequence-driven behavior.

## 12.4 Remote Interaction [SEC:UDQ-UI-MOD-001::12.4]
Remote-origin actions shall be visible as remote-origin actions. A local UI shall not imply exclusive control if remote supervision is active.

## 12.5 Safe-State Supremacy [SEC:UDQ-UI-MOD-001::12.5]
When safe-state doctrine supersedes other command origins, the UI shall show this clearly and explain why other requests are not taking effect.

## 13. Startup and Restore Behavior [SEC:UDQ-UI-MOD-001::13]

## 13.1 What Shall Restore [SEC:UDQ-UI-MOD-001::13.1]
The UI should restore, where appropriate:
- shell/window geometry,
- dock arrangement,
- selected workspaces/tabs,
- trend layout preferences,
- local visibility/style preferences,
- recent filters and inspectors,
- local draft objects not yet applied,
- selected profiles where appropriate.

## 13.2 What Shall Not Be Assumed Restored as Truth [SEC:UDQ-UI-MOD-001::13.2]
The UI shall not assume that the following are restored as current truth merely because prior local state existed:
- active output values,
- active device enable state,
- active ownership state,
- active sequence state,
- current rule activation state,
- current alarm acknowledgment state,
- current live backend connectivity state.

## 13.3 Restore Reconciliation [SEC:UDQ-UI-MOD-001::13.3]
After restore, the UI shall reconcile restored local context with live backend state and indicate mismatches where relevant.

## 13.4 Autosave / Dirty-State Model [SEC:UDQ-UI-MOD-001::13.4]
Local UI state and draft artifacts may autosave, but dirty-state visibility shall exist for important unsaved changes where user understanding depends on it.

## 14. Disconnect and Reconnect Behavior [SEC:UDQ-UI-MOD-001::14]

## 14.1 Device Disconnect [SEC:UDQ-UI-MOD-001::14.1]
If an individual device disconnects while the backend remains alive, the UI shall localize that impairment rather than globally implying total system loss.

## 14.2 Backend Disconnect [SEC:UDQ-UI-MOD-001::14.2]
If backend disconnects, live control surfaces shall degrade accordingly. Review and local draft capabilities may remain where safe.

## 14.3 Reconnect [SEC:UDQ-UI-MOD-001::14.3]
On reconnect the UI shall:
- refresh authoritative state,
- reconcile ownership and active execution state,
- update stale last-known values to current values where available,
- avoid silently replaying unsafe prior actions,
- preserve local draft edits unless explicitly invalidated.

## 15. Runtime Execution Interaction Model [SEC:UDQ-UI-MOD-001::15]

## 15.1 Sequences [SEC:UDQ-UI-MOD-001::15.1]
When a sequence is running, the UI shall show:
- active sequence identity,
- active step/state,
- progress or hold condition,
- whether the instance is paused, running, completed, aborted, faulted, or blocked,
- whether a local edit is changing a draft only or affecting the active runtime instance.

## 15.2 Rules [SEC:UDQ-UI-MOD-001::15.2]
When rules are active, the UI shall support visibility into:
- whether a rule is enabled,
- whether it is currently true/false/unknown,
- which subconditions are failing,
- whether its action is being requested,
- whether its requested action is effective or overridden.

## 15.3 Outputs [SEC:UDQ-UI-MOD-001::15.3]
When outputs are active, the UI shall reflect not only value but authority context, quality of feedback, and whether the observed field state matches the resolved backend target.

## 16. Historical Review and Live Comparison Behavior [SEC:UDQ-UI-MOD-001::16]
The UI shall permit users to inspect prior runs, prior sessions, and historical trends without compromising awareness of current runtime status.

Where the UI allows simultaneous presentation of historical review and live state, the distinction shall remain explicit in labels, timestamps, and interaction cues.

## 17. Remote Observation and Supervision Interaction Model [SEC:UDQ-UI-MOD-001::17]

## 17.1 Remote Observation [SEC:UDQ-UI-MOD-001::17.1]
Remote observation clients shall be able to inspect allowed live and historical material without implying write authority.

## 17.2 Remote Supervision [SEC:UDQ-UI-MOD-001::17.2]
Where enabled, remote supervision clients may request bounded supervisory actions. The UI shall show such requests as remote-origin requests and preserve auditability.

## 17.3 Remote Direct Control [SEC:UDQ-UI-MOD-001::17.3]
Remote direct control, if ever allowed in a given deployment, shall be more constrained and visibly distinct from mere remote observation. The local UI shall not conceal the existence of remote-capable authority.

## 17.4 Multi-Client Awareness [SEC:UDQ-UI-MOD-001::17.4]
The interaction model shall anticipate that more than one UI client may exist. Backend arbitration remains the convergence point. UI clients shall not behave as though they are solitary owners by default.

## 18. Diagnostics and Explainability Interaction Model [SEC:UDQ-UI-MOD-001::18]
The UI shall provide explainability surfaces sufficient for a technical user to answer questions such as:
- Why is this value stale?
- Why is this output not changing?
- Who currently owns this point?
- Why is this rule false?
- Why can’t this sequence proceed?
- Why is this device read-only?
- Why is this command blocked?
- What changed since last good operation?

This explainability shall be available without requiring users to infer everything from raw logs alone.

## 19. Error, Warning, and Confirmation Behavior [SEC:UDQ-UI-MOD-001::19]

## 19.1 Errors [SEC:UDQ-UI-MOD-001::19.1]
Errors shall be specific enough to support corrective action rather than generic failure wording.

## 19.2 Warnings [SEC:UDQ-UI-MOD-001::19.2]
Warnings shall identify degraded trust or pending risk without overstating certainty.

## 19.3 Confirmations [SEC:UDQ-UI-MOD-001::19.3]
Confirmation prompts shall be used where control significance, irreversibility, or safety relevance justify them. Routine interaction shall not be made unusably slow by over-confirmation.

## 19.4 Silent Failure Prohibition [SEC:UDQ-UI-MOD-001::19.4]
The UI shall not silently drop important user actions, command requests, restore failures, or validation failures where user understanding materially depends on the result.

## 20. Anti-Patterns Prohibited by This Model [SEC:UDQ-UI-MOD-001::20]
The following are prohibited:
- UI showing restored last session values as if they are current machine truth before live reconciliation.
- UI displaying pending commands as accomplished state.
- Historical review views visually masquerading as live runtime views.
- Simulated/test data visually blending with normal live control data.
- Hidden output ownership or untraceable blocking of commands.
- Editing active runtime objects without clearly distinguishing draft-from-live effects.
- Implicit assumption that local UI is sole command origin in a multi-client system.
- Frontend-only edits that appear committed without validation/activation path.

## 21. Downstream Consequences [SEC:UDQ-UI-MOD-001::21]
This document shall drive later detailed specifications for:
- workspace-specific page and workflow definitions,
- rule editor interaction design,
- sequence execution supervision UI,
- device/protocol editing flows,
- historian/live comparison workflows,
- remote client behavior,
- validation and apply workflows,
- command and ownership visualization,
- session restore and profile handling,
- requirements traceability updates,
- definition-of-complete updates.

## 22. Definition of Complete for This Document [SEC:UDQ-UI-MOD-001::22]
This document shall be considered working-complete when it is accepted as the governing interaction model for future UI detailed specifications and is reconciled into the updated architecture, requirements, and completion documents.
