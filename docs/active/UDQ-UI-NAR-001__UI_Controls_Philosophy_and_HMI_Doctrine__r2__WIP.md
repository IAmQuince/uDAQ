---
document_id: UDQ-UI-NAR-001
title: UI Controls Philosophy and HMI Doctrine
revision: r2
status: WIP
document_class: ui_doctrine
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-LOG-001
  - UDQ-ARCH-NAR-001
  - UDQ-ARCH-NAR-002
  - UDQ-REQ-MAT-001
  - UDQ-QUAL-DEF-001
  - UDQ-UI-INV-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-SPEC-006
supersedes:
  - UDQ-UI-NAR-001__UI_Controls_Philosophy_and_HMI_Doctrine__r1__WIP.md
---

# UI Controls Philosophy and HMI Doctrine [SEC:UDQ-UI-NAR-001::0]

## Revision History [SEC:UDQ-UI-NAR-001::0.1]
- r2: Docs-only UI refinement pass. Reframed Genesys as inspiration rather than inheritance, formalized the four-workspace model, introduced the Control workspace doctrine, and made validation/simulation/audit first-class trust mechanisms.
- r1: Machine-readable normalization pass, unique section anchors, metadata cleanup, and content polish against the current governed corpus.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-UI-NAR-001::1]

This document defines the governing philosophy and doctrine for the UniversalDAQ user interface and human-machine interface. It establishes what the UI is for, what responsibilities it carries, what responsibilities it does not carry, how it shall relate to backend authority, and what design obligations follow from UniversalDAQ being both a data-acquisition platform and a supervisory control platform.

This doctrine is intended to prevent drift toward device-specific page design, ambiguous operator experiences, control authoring that cannot be trusted, and frontend behavior that silently conflicts with backend truth.

This document is not a pixel-level mockup, widget catalog, or implementation guide. It is the governing doctrine that later UI architecture, interaction, requirements, and verification documents shall follow.

## 2. Scope [SEC:UDQ-UI-NAR-001::2]

This doctrine applies to all UniversalDAQ UI surfaces, including but not limited to:

- local desktop application surfaces
- docked and floating panes
- live runtime workspaces
- control-authoring workspaces
- historical and evidence review surfaces
- diagnostics, service, and onboarding surfaces
- remote observer and remote supervisor surfaces
- print/export-oriented UI representations where the operator experience is preserved

## 3. Foundational Position [SEC:UDQ-UI-NAR-001::3]

UniversalDAQ is a universal signal, control, review, and evidence platform. The UI therefore shall not be organized around any one vendor, instrument, process domain, or earlier application shell. It shall instead be organized around the stable operator chain:

**observe signals → derive values → make decisions → issue actions → verify outcomes**

The UI shall make that chain understandable, inspectable, and reviewable.

The backend remains authoritative for execution truth, command admission, and governed state transitions. The UI remains authoritative for operator comprehension, authoring ergonomics, evidence visibility, and honest representation of system truth.

## 4. Design Principles [SEC:UDQ-UI-NAR-001::4]

### 4.1 Backend authority [SEC:UDQ-UI-NAR-001::4.1]
The UI shall not quietly become a second execution engine or a hidden authority source. It may summarize, preview, stage, validate, simulate, or explain. It shall not redefine machine truth.

### 4.2 Human clarity over internal convenience [SEC:UDQ-UI-NAR-001::4.2]
The UI shall be organized around human questions and operational tasks rather than around internal class boundaries or protocol plumbing.

### 4.3 No ambiguous state presentation [SEC:UDQ-UI-NAR-001::4.3]
Live, stale, invalid, historical, simulated, blocked, draft, deployed, requested, applied, and observed state shall remain visibly distinct.

### 4.4 Traceable control behavior [SEC:UDQ-UI-NAR-001::4.4]
A user shall be able to determine what inputs were used, what rule or sequence fired, what action was requested, and what outcome was observed.

### 4.5 Safe defaults [SEC:UDQ-UI-NAR-001::4.5]
The UI shall favor bounded, confirmable, reversible, and explainable actions over fast but ambiguous shortcuts.

### 4.6 Dense engineering usability [SEC:UDQ-UI-NAR-001::4.6]
The UI shall support professional, dense, engineering-grade workflows. Dense shall not mean cryptic. Power and clarity shall coexist.

### 4.7 Preserve proven operator patterns [SEC:UDQ-UI-NAR-001::4.7]
Successful operator patterns from earlier tools may be preserved when they are generalized into device-agnostic UniversalDAQ concepts.

### 4.8 Generalize, do not clone [SEC:UDQ-UI-NAR-001::4.8]
Earlier tools may inspire graph posture, docking, or review ergonomics, but UniversalDAQ shall not inherit their device assumptions, page taxonomy, or naming as architectural constraints.

### 4.9 Explainability is not optional [SEC:UDQ-UI-NAR-001::4.9]
Explainability is not merely a diagnostics feature. It is part of the primary operator trust contract.

### 4.10 Remote clients are not exceptions [SEC:UDQ-UI-NAR-001::4.10]
Remote surfaces shall obey the same truth, authority, and evidence doctrines as local surfaces, while honestly presenting narrower capability where policy requires it.

## 5. UI Mission [SEC:UDQ-UI-NAR-001::5]

The mission of the UniversalDAQ UI is to let users:

- understand current runtime state
- configure and inspect devices and signals
- author dependable control behavior
- verify and explain decisions and actions
- review evidence over time
- recover continuity without conflating restored UI state with machine truth

## 6. Users and Operating Contexts [SEC:UDQ-UI-NAR-001::6]

The UI shall support at least the following operator contexts:

### 6.1 Commissioning and setup [SEC:UDQ-UI-NAR-001::6.1]
Discovering devices, naming points, establishing bindings, confirming capabilities, and defining the first controlled values.

### 6.2 Runtime supervision [SEC:UDQ-UI-NAR-001::6.2]
Watching live trends, alarms, values, and device health while preserving immediate return to live operation after review.

### 6.3 Direct/manual control [SEC:UDQ-UI-NAR-001::6.3]
Issuing bounded human actions with explicit ownership, requested-versus-observed feedback, and safe-state visibility.

### 6.4 Control authoring [SEC:UDQ-UI-NAR-001::6.4]
Defining variables, logic, sequences, protections, actions, modes, tests, and audit history in a coherent workspace rather than in disconnected mini-editors.

### 6.5 Diagnostics and service [SEC:UDQ-UI-NAR-001::6.5]
Inspecting dependencies, communication health, validation failures, runtime evidence, and degraded states.

### 6.6 Remote observation [SEC:UDQ-UI-NAR-001::6.6]
Reviewing values, graphs, alarms, and evidence without being misled into thinking local parity exists.

### 6.7 Remote supervision [SEC:UDQ-UI-NAR-001::6.7]
Performing allowed acknowledgments or bounded supervisory actions with explicit attribution and policy-bounded capability.

## 7. Primary Workspace Doctrine [SEC:UDQ-UI-NAR-001::7]

### 7.1 Primary layout [SEC:UDQ-UI-NAR-001::7.1]
The primary shell shall remain graph-centered, with dockable side tooling, an evidence-oriented lower pane, and optional detail inspection surfaces.

### 7.2 Rationale [SEC:UDQ-UI-NAR-001::7.2]
A graph-centered shell supports runtime comprehension, review, and evidence-driven debugging. It shall remain the home surface because it keeps the operator close to truth over time.

### 7.3 Non-requirement for fixed page cloning [SEC:UDQ-UI-NAR-001::7.3]
UniversalDAQ does not need to reproduce the page taxonomy of any earlier tool. It shall preserve useful patterns, not previous page identities.

### 7.4 Workspace orientation [SEC:UDQ-UI-NAR-001::7.4]
The top-level workspace posture shall be:
- **Run** for live supervision and direct bounded action
- **Control** for authoring and validating control assets
- **Review** for historian, evidence, and forensic exploration
- **System** for devices, diagnostics, profiles, and configuration

## 8. Functional UI Domains [SEC:UDQ-UI-NAR-001::8]

### 8.1 Run [SEC:UDQ-UI-NAR-001::8.1]
Run is the operational home surface. It emphasizes live signals, graphing, bounded command issuance, active protections, current sequence state, and immediate return to live after exploration.

### 8.2 Control [SEC:UDQ-UI-NAR-001::8.2]
Control is the governed authoring environment. It is not merely a rules editor or a sequencer page. It is where users define the logic system they intend to trust.

### 8.3 Review [SEC:UDQ-UI-NAR-001::8.3]
Review is where historical evidence, event timelines, command outcomes, graph exploration, and annotations are gathered and correlated.

### 8.4 System [SEC:UDQ-UI-NAR-001::8.4]
System is where device onboarding, protocol details, diagnostics, profile handling, and service-state inspection live.

## 9. Control Authoring Doctrine [SEC:UDQ-UI-NAR-001::9]

### 9.1 Governed asset chain [SEC:UDQ-UI-NAR-001::9.1]
Control authoring shall make explicit the chain from signals to variables to logic to actions to observed outcomes.

### 9.2 Structured-first authoring [SEC:UDQ-UI-NAR-001::9.2]
The default authoring posture shall be structured rows, cards, forms, and inspectors. Large free-form canvases may exist as secondary views, not as the only primary authoring surface.

### 9.3 Sequence as supporting feature [SEC:UDQ-UI-NAR-001::9.3]
Sequence authoring remains a required feature, but it is not the sole control metaphor. It shall remain available as a convenient procedural surface for timed steps, ramps, setpoint changes, external outputs, and internal or virtual variables.

### 9.4 Protections are distinct [SEC:UDQ-UI-NAR-001::9.4]
Interlocks, permissives, trips, and protections shall not be buried inside ordinary logic lists such that users cannot easily inspect or audit them.

### 9.5 Explainability at authoring time [SEC:UDQ-UI-NAR-001::9.5]
The user shall be able to inspect dependencies, validation results, and last-known runtime behavior from within the authoring environment.

### 9.6 Simulation and audit are first-class [SEC:UDQ-UI-NAR-001::9.6]
Validation, test/simulation, draft-versus-deployed comparison, and audit history are part of the authoring contract, not optional extras.

## 10. Authority and Command Doctrine [SEC:UDQ-UI-NAR-001::10]

### 10.1 Backend arbitration [SEC:UDQ-UI-NAR-001::10.1]
All command-capable UI surfaces shall respect backend arbitration and policy.

### 10.2 Visible ownership [SEC:UDQ-UI-NAR-001::10.2]
The operator shall be able to tell whether a point is under manual, logic, sequence, remote, or other authority.

### 10.3 Requests vs final application [SEC:UDQ-UI-NAR-001::10.3]
The UI shall clearly distinguish between a requested action and an observed effect.

### 10.4 Conflict visibility [SEC:UDQ-UI-NAR-001::10.4]
Blocked actions, conflicting claims, inhibited operations, and missing confirmations shall remain visible.

### 10.5 Manual distinctness [SEC:UDQ-UI-NAR-001::10.5]
Manual action shall remain visibly distinct from automated or remote action.

### 10.6 Confirmation and boundedness [SEC:UDQ-UI-NAR-001::10.6]
Consequential actions shall use confirmation flows appropriate to their risk and reversibility.

## 11. State Representation Doctrine [SEC:UDQ-UI-NAR-001::11]

### 11.1 Required distinguishable states [SEC:UDQ-UI-NAR-001::11.1]
The UI shall distinguish at least:
- live
- stale
- invalid
- disconnected
- simulated
- historical
- draft
- deployed
- blocked or interlocked
- pending validation
- pending apply
- requested
- observed
- acknowledged
- latched or tripped
- manual, sequence, rule, or remote authority

### 11.2 No visual conflation [SEC:UDQ-UI-NAR-001::11.2]
No state may rely on color alone for distinction. Badges, icons, text labels, or other durable cues shall accompany color where state matters.

### 11.3 Historical vs live separation [SEC:UDQ-UI-NAR-001::11.3]
A user shall not mistake explored history for live runtime just because the same graphing surface is reused.

### 11.4 Simulated/test clarity [SEC:UDQ-UI-NAR-001::11.4]
Simulation and replay shall remain visually distinct from live execution.

### 11.5 Quality-aware logic visibility [SEC:UDQ-UI-NAR-001::11.5]
Missing, stale, or invalid upstream values shall be inspectable where they affect downstream variables, rules, or actions.

## 12. Graph Doctrine [SEC:UDQ-UI-NAR-001::12]

### 12.1 Graph centrality [SEC:UDQ-UI-NAR-001::12.1]
The graph remains central because it is the clearest runtime evidence surface.

### 12.2 Required graph modes [SEC:UDQ-UI-NAR-001::12.2]
The graph shall support live follow, sliding-window live view, whole-history review, free explore, and one-click return to live.

### 12.3 Evidence overlays [SEC:UDQ-UI-NAR-001::12.3]
The graph shall support overlays for events, alarms, commands, rule firings, sequence transitions, notes, and similar evidence markers where relevant.

### 12.4 Truthful review [SEC:UDQ-UI-NAR-001::12.4]
Downsampling, decimation, and evidence selection shall remain honest. The user shall be able to understand what time range and density they are seeing.

## 13. Device and Protocol Doctrine [SEC:UDQ-UI-NAR-001::13]

### 13.1 Devices are first-class objects [SEC:UDQ-UI-NAR-001::13.1]
Devices shall be represented as identifiable objects with capabilities, lifecycle, and health.

### 13.2 Protocol abstraction [SEC:UDQ-UI-NAR-001::13.2]
Protocol specifics shall be available without making ordinary users reason in raw protocol detail all the time.

### 13.3 Advanced views are allowed [SEC:UDQ-UI-NAR-001::13.3]
Raw or protocol-oriented detail is allowed in advanced views where it improves serviceability.

## 14. Persistence and Operator Continuity Doctrine [SEC:UDQ-UI-NAR-001::14]

### 14.1 Workspace continuity [SEC:UDQ-UI-NAR-001::14.1]
Layout, tabs, graph selections, and inspector posture may be restored to preserve human continuity.

### 14.2 Separation from machine truth [SEC:UDQ-UI-NAR-001::14.2]
Restored UI state shall never be presented as restored machine truth without live reconciliation.

### 14.3 Layout preference [SEC:UDQ-UI-NAR-001::14.3]
Dock placement, including whether the primary rail is left-docked or right-docked, shall be a persistent user preference.

### 14.4 Safe restoration behavior [SEC:UDQ-UI-NAR-001::14.4]
Any restored draft or staged edit shall remain visibly staged until validated and intentionally applied.

## 15. Diagnostics and Explainability Doctrine [SEC:UDQ-UI-NAR-001::15]

The UI shall make it practical to answer:
- what changed
- why it changed
- what inputs were used
- what blocked a change
- whether the action was only requested or actually observed
- whether the behavior came from manual action, rule logic, sequence execution, or remote action

The lower pane, evidence panels, audit/history surfaces, and graph overlays shall work together to answer those questions without forcing the user into raw logs alone.

## 16. Genesys Preservation Doctrine [SEC:UDQ-UI-NAR-001::16]

UniversalDAQ preserves the following classes of operator value from the earlier Genesys application line:

- graph-first operating posture
- dockable engineering workspace ergonomics
- sliding-window live view plus free exploration and return to live
- dense, professional, non-consumer interaction style
- convenient procedural sequencing for outputs and internal variables

UniversalDAQ does **not** inherit:
- fixed page taxonomy
- device-specific surfaces as architectural primitives
- naming or structure tied to one earlier tool
- any assumption that the sequencer is the sole or dominant control authoring model

## 17. Summary [SEC:UDQ-UI-NAR-001::17]

The UniversalDAQ UI shall be a graph-centered, workspace-based, evidence-oriented engineering environment. It shall let the user supervise runtime truth, author dependable control logic, inspect dependencies, validate and simulate behavior, review evidence over time, and return to live operation without confusion. It shall preserve the useful ergonomics of earlier tools without being architecturally bound to them.
