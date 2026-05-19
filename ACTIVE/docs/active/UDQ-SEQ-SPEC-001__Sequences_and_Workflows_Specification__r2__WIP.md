---
document_id: UDQ-SEQ-SPEC-001
title: Sequences and Workflows Specification
revision: r2
status: WIP
document_class: subsystem_spec
owner: UniversalDAQ
depends_on:
  - "UDQ-ARCH-NAR-001"
  - "UDQ-ARCH-NAR-002"
  - "UDQ-UI-NAR-001"
  - "UDQ-UI-ARCH-001"
  - "UDQ-UI-MOD-001"
  - "UDQ-LOG-SPEC-001"
  - "UDQ-SIG-SPEC-001"
  - "UDQ-OUT-SPEC-001"
  - "UDQ-PROT-SPEC-001"
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-STD-002"
supersedes:
  - "UDQ-SEQ-SPEC-001__Sequences_and_Workflows_Specification__r1__WIP.md"
revision_history:
  - "r2 | 2026-03-21 | Subsystem reconciliation pass: clarified sequence ownership, emitted-request semantics, and runtime-state distinctions."
  - "r1 | 2026-03-21 | Prior active revision carried forward before subsystem reconciliation pass."
---
# Sequences and Workflows Specification [SEC:UDQ-SEQ-SPEC-001::0]

## Revision History [SEC:UDQ-SEQ-SPEC-001::0.1]
- r2: Subsystem reconciliation pass: clarified sequence ownership, emitted-request semantics, and runtime-state distinctions.
- r1: Machine-readable normalization pass, unique section anchors, metadata cleanup, and content polish against the current governed corpus.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-SEQ-SPEC-001::1]
This document defines the UniversalDAQ sequence and workflow model. It specifies how ordered operational procedures, semi-automatic routines, operator-guided workflows, and reusable process logic shall be represented, validated, executed, supervised, interrupted, resumed, explained, and audited.

The goal is to preserve the practical value already demonstrated in the Genesys sequence interface while generalizing it into a platform-level model that can supervise broader device sets, rules, outputs, remote monitoring, and historian-backed evidence.

## 2. Scope [SEC:UDQ-SEQ-SPEC-001::2]
This specification covers:
- canonical sequence/workflow objects
- step types and transition semantics
- execution state model
- interaction with signals, rules, outputs, devices, and Modbus-backed points
- pause/hold/abort/reset behavior
- restart/resume/recovery expectations
- UI supervision requirements
- explainability, historian, eventing, and audit requirements

This specification does not define:
- exact page layouts or widget styling
- arbitrary user scripting engines
- low-level device-driver internals
- plant-specific procedure libraries

## 2A. Semantic Closure and Anti-Conflation Rule [SEC:UDQ-SEQ-SPEC-001::2A]

Sequences may own execution context and may emit governed requests, but they do not escape authorization, arbitration, or evidence rules. Sequence definition, revision, runtime instance, ownership, pause/hold/abort state, and emitted actions shall remain distinguishable. Sequence success shall not be inferred from request issuance alone when observed confirmation is available.

## 3. Foundational Position [SEC:UDQ-SEQ-SPEC-001::3]
UniversalDAQ sequences shall be treated as supervised, backend-owned execution objects.

A sequence is not merely a frontend playlist and is not allowed to become an unbounded scripting environment. A sequence issues structured requests, evaluates conditions, tracks progress, and records evidence while remaining subordinate to backend arbitration, interlocks, permissives, and safe-state doctrine.

A sequence may coordinate actions across multiple devices and outputs, but it shall never bypass canonical output ownership, rule evaluation policy, or safety policy.

## 4. Conceptual Model [SEC:UDQ-SEQ-SPEC-001::4]
UniversalDAQ shall distinguish the following related concepts:

## 4.1 Sequence Definition [SEC:UDQ-SEQ-SPEC-001::4.1]
A reusable authored procedure consisting of ordered steps, transitions, parameters, policies, and metadata.

## 4.2 Sequence Instance [SEC:UDQ-SEQ-SPEC-001::4.2]
A runtime execution instance of a sequence definition, with live state, timestamps, parameter bindings, current step, execution history, and final outcome.

## 4.3 Workflow [SEC:UDQ-SEQ-SPEC-001::4.3]
A broader operational pattern that may include one or more sequences plus operator tasks, configuration tasks, validation gates, review checkpoints, or post-run evidence actions.

## 4.4 Step [SEC:UDQ-SEQ-SPEC-001::4.4]
A discrete execution unit inside a sequence. A step may wait, command, validate, branch, notify, prompt, or delegate to another reusable sequence.

## 4.5 Transition [SEC:UDQ-SEQ-SPEC-001::4.5]
The condition under which control advances from one step to another. A transition may be immediate, time-based, condition-based, operator-confirmed, or outcome-based.

## 4.6 Hold Point [SEC:UDQ-SEQ-SPEC-001::4.6]
A designed pause boundary where continuation requires an explicit condition, acknowledgment, permission, or operator action.

## 4.7 Abort Path [SEC:UDQ-SEQ-SPEC-001::4.7]
A defined path for stopping execution in an orderly way when a fault, interlock, operator command, timeout, or policy violation occurs.

## 5. Canonical Sequence Object [SEC:UDQ-SEQ-SPEC-001::5]
A canonical sequence definition shall include at minimum:
- stable sequence ID
- display name
- revision identity
- description/purpose
- enabled/disabled status
- authoring metadata
- parameter definitions
- ordered step graph
- allowed entry point(s)
- default start step
- completion policy
- pause/hold/abort policy
- retry/restart policy
- dependency references
- notes and audit metadata

A canonical sequence instance shall include at minimum:
- stable runtime instance ID
- bound sequence definition ID and revision
- start timestamp
- end timestamp when complete
- launch source/origin
- bound parameter values
- execution status
- current step
- step history with timestamps
- transition history
- requests issued
- waits/holds/timeouts encountered
- abort/fault reasons if applicable
- final outcome classification

## 6. Authoring Model [SEC:UDQ-SEQ-SPEC-001::6]
Sequences shall be authored as structured objects, not as opaque code blobs.

The platform shall support a no-code authoring model first. A future advanced representation may be added later, but the canonical model shall remain structured and round-trippable.

Authoring shall support:
- ordered steps
- reorder/move operations
- named reusable parameters
- explicit transition conditions
- step-local notes
- expected time annotations where useful
- validation before activation
- dependency cross-reference visibility

Sequence definitions shall be revisioned. A running sequence instance shall remain bound to the revision from which it started unless an explicit migration model is later defined.

## 7. Step Types [SEC:UDQ-SEQ-SPEC-001::7]
The platform shall support a constrained, explicit set of step types.

## 7.1 Informational/Prompt Step [SEC:UDQ-SEQ-SPEC-001::7.1]
Presents instruction, caution, or required operator action. May require acknowledgment or data entry before advance.

## 7.2 Wait Step [SEC:UDQ-SEQ-SPEC-001::7.2]
Waits for a duration, absolute time boundary, or dwell period.

## 7.3 Condition Wait Step [SEC:UDQ-SEQ-SPEC-001::7.3]
Waits until a signal, derived signal, rule state, device state, or expression becomes satisfied.

## 7.4 Command Step [SEC:UDQ-SEQ-SPEC-001::7.4]
Issues one or more structured command requests to canonical outputs, devices, or sequence-managed actions.

## 7.5 Verification Step [SEC:UDQ-SEQ-SPEC-001::7.5]
Checks that expected state was reached after a command or external event.

## 7.6 Branch Step [SEC:UDQ-SEQ-SPEC-001::7.6]
Chooses a transition path based on defined condition results.

## 7.7 Set Parameter / Compute Value Step [SEC:UDQ-SEQ-SPEC-001::7.7]
Assigns or computes a local sequence variable or parameter value using approved functions.

## 7.8 Subsequence Step [SEC:UDQ-SEQ-SPEC-001::7.8]
Invokes another sequence definition as a child operation under controlled rules.

## 7.9 Event/Marker Step [SEC:UDQ-SEQ-SPEC-001::7.9]
Creates a named event marker in the historian/event stream for later analysis or reporting.

## 7.10 Acquire Snapshot Step [SEC:UDQ-SEQ-SPEC-001::7.10]
Captures a defined evidence set, such as selected signals, device states, or configuration state.

## 7.11 Manual Hold / Approval Step [SEC:UDQ-SEQ-SPEC-001::7.11]
Requires explicit operator or supervisory approval before continuation.

Future step types may be added, but all shall map cleanly to the canonical execution model.

## 8. Transition Semantics [SEC:UDQ-SEQ-SPEC-001::8]
Transitions shall be explicit.

Each step shall define one or more transition paths. The system shall not rely on hidden implicit jumps except for clearly defined completion/failure defaults.

Supported transition triggers shall include:
- immediate success
- duration elapsed
- condition satisfied
- operator confirmed
- verification passed
- verification failed
- timeout
- fault/interlock/inhibit encountered
- abort request received

Where multiple transitions are possible, the evaluation order or priority shall be explicit and explainable.

## 9. Execution State Model [SEC:UDQ-SEQ-SPEC-001::9]
Each sequence instance shall expose a clear execution state.

Minimum top-level states shall include:
- Draft
- Validated
- Ready
- Starting
- Running
- Holding
- Paused
- Waiting
- Awaiting Confirmation
- Completing
- Completed
- Aborting
- Aborted
- Faulted
- Invalidated

State meaning shall be consistent across the platform and visible in the UI.

## 10. Step Runtime State [SEC:UDQ-SEQ-SPEC-001::10]
Each individual step shall expose runtime state such as:
- Not Entered
- Entering
- Active
- Waiting
- Satisfied
- Timed Out
- Failed Verification
- Skipped
- Completed
- Aborted

The platform shall retain enough runtime detail to explain why a step advanced, held, failed, skipped, or aborted.

## 11. Parameters and Bindings [SEC:UDQ-SEQ-SPEC-001::11]
Sequences shall support reusable parameters.

Parameters may include:
- numeric setpoints
- booleans
- enumerated choices
- durations
- references to named signals or devices where permitted
- operator-entered notes or batch identifiers where appropriate

Parameter validation shall occur before sequence activation.

The platform shall distinguish:
- definition-time defaults
- launch-time overrides
- runtime frozen values
- explicitly mutable runtime values, if supported for a given parameter

Runtime mutation shall be tightly controlled and clearly visible.

## 12. Relationship to Signals and Derived Signals [SEC:UDQ-SEQ-SPEC-001::12]
Sequences shall consume canonical signals and derived signals, not raw ad hoc device values whenever normalized signals exist.

A sequence may:
- wait on signals
- branch on signals
- verify expected signal states
- capture evidence snapshots of signals
- annotate step transitions with observed signal values

Signal quality shall matter. If a step depends on stale, invalid, blocked, or disconnected signal state, the platform shall handle that explicitly rather than silently treating it as false.

## 13. Relationship to Rules and Conditions [SEC:UDQ-SEQ-SPEC-001::13]
Sequences and the rules engine shall be distinct but interoperable.

Rules represent reusable logic and supervisory conditions.
Sequences represent ordered procedural execution.

A sequence may:
- reference rule states as conditions
- request temporary modes that rules can observe
- be inhibited by rules, interlocks, or permissives
- emit sequence-state signals for rules or UI consumption

A sequence shall not bypass rule visibility, and a rule shall not invisibly rewrite sequence progress.

## 14. Relationship to Outputs and Arbitration [SEC:UDQ-SEQ-SPEC-001::14]
Sequence command steps shall issue command requests into the canonical output arbitration framework.

A sequence shall not directly force applied hardware state outside the output model.

Sequence-originated requests shall:
- carry origin/ownership attribution
- be visible as sequence-owned or sequence-requested
- remain subject to interlocks, permissives, inhibits, safe-state policy, and higher-priority ownership
- provide feedback on requested vs applied vs blocked outcome

The UI shall make clear when a sequence is requesting an output that was denied, delayed, clamped, or overridden.

## 15. Safe-State, Fault, and Abort Behavior [SEC:UDQ-SEQ-SPEC-001::15]
A sequence specification shall define how faults and aborts are handled.

At minimum, the platform shall distinguish:
- graceful completion
- graceful abort
- forced abort due to fault/interlock/safe-state
- hold awaiting operator intervention
- invalidation due to lost prerequisite context

A sequence may define cleanup/exit steps, but these remain subordinate to safe-state doctrine.

If the backend enters a global safe-state condition, sequence execution shall transition in a deterministic and explainable manner. Sequence logic shall not continue blindly after a system-level protective action.

## 16. Pause, Hold, Resume, and Reset [SEC:UDQ-SEQ-SPEC-001::16]
The platform shall distinguish the following:

## 16.1 Pause [SEC:UDQ-SEQ-SPEC-001::16.1]
An operator- or supervisor-requested temporary stop in forward progress, typically intended to be resumed.

## 16.2 Hold [SEC:UDQ-SEQ-SPEC-001::16.2]
A designed or condition-triggered stop where explicit criteria must be met before continuation.

## 16.3 Resume [SEC:UDQ-SEQ-SPEC-001::16.3]
Continuation of a paused or held sequence after validation of current context.

## 16.4 Reset [SEC:UDQ-SEQ-SPEC-001::16.4]
Return of the runtime instance to a non-running state. Reset shall not imply restoration of plant state.

Resume shall require context revalidation where necessary, especially after disconnect/reconnect, safe-state entry, remote-client changes, or output ownership changes.

## 17. Restart and Recovery [SEC:UDQ-SEQ-SPEC-001::17]
The system shall define recovery expectations for abnormal interruption.

Potential interruption cases include:
- UI disconnect while backend remains active
- local UI close with backend still running
- backend restart
- device disconnect/reconnect
- safe-state event
- remote supervisory intervention

The platform shall distinguish:
- sequence definition recovery
- runtime instance recovery
- operator review-only reconstruction
- resumable execution

Resumption after backend restart shall not be assumed by default unless a later design explicitly supports persistent resumable instances.

## 18. Timing and Timeouts [SEC:UDQ-SEQ-SPEC-001::18]
Sequence timing shall be first-class.

The platform shall support:
- dwell times
- wait deadlines
- step-level timeout policies
- sequence-level timeout policies where appropriate
- expected duration annotations
- elapsed-time visibility

Timeout is not the same as false condition. Timeout handling shall be explicit and auditable.

## 19. Sequence Modes [SEC:UDQ-SEQ-SPEC-001::19]
The platform may support different launch or runtime modes such as:
- simulation/test mode
- advisory mode
- supervised live mode
- unattended authorized mode

Mode semantics shall be explicit. Simulated or advisory sequence execution shall never be visually confused with live hardware-affecting execution.

## 20. UI Obligations [SEC:UDQ-SEQ-SPEC-001::20]
The UI shall provide strong sequence supervision rather than merely a start/stop button.

At minimum the UI shall support:
- sequence library browsing
- revision visibility
- parameter entry and validation
- step list/graph visibility
- current step highlight
- elapsed time and timers
- transition reason visibility
- hold/pause/abort/resume controls as permitted
- live output/request trace for sequence-owned actions
- blocked/interlock/fault visibility
- evidence/event markers during execution
- post-run review of what happened and why

The Genesys-style sequence view and preview pattern shall be preserved in spirit, but generalized to the canonical model.

## 21. Explainability and Traceability [SEC:UDQ-SEQ-SPEC-001::21]
Sequence execution shall be explainable.

For each running or completed instance, the platform shall be able to show:
- what step is/was active
- why the step was entered
- why it advanced or failed to advance
- which conditions were satisfied or blocking
- what requests were issued
- whether those requests were applied or blocked
- what signal values or device states were observed at key transitions
- who/what launched, paused, resumed, or aborted the sequence

A user shall not be left with only “step 4 failed” without underlying reasons.

## 22. Historian, Eventing, and Evidence [SEC:UDQ-SEQ-SPEC-001::22]
Sequence execution shall integrate with historian and event systems.

The platform shall record at minimum:
- sequence start/stop times
- step enter/exit times
- pause/hold/resume/abort events
- parameter set used for the run
- major command requests issued
- verification pass/fail outcomes
- timeout events
- evidence snapshots where configured

Sequence events shall be searchable and attributable.

## 23. Validation Requirements [SEC:UDQ-SEQ-SPEC-001::23]
A sequence definition shall be validated before activation.

Validation shall include at minimum:
- unresolved signal/device/output references
- illegal step transitions
- invalid timeout or timing configuration
- parameter type/default errors
- illegal subsequence recursion or cycle risk
- output request capability mismatch
- forbidden action types for deployment policy
- unreachable steps where relevant
- missing abort/termination handling where policy requires it

Validation results shall be visible and actionable.

## 24. Dependency and Reuse Policy [SEC:UDQ-SEQ-SPEC-001::24]
Sequences may depend on:
- signals
- derived signals
- rules
- outputs
- device capabilities
- subsequences
- named workflow templates

Dependency visibility shall be first-class so users can understand impact when a referenced object changes.

Reusable patterns are encouraged, but hidden implicit coupling is forbidden.

## 25. Remote Supervision Implications [SEC:UDQ-SEQ-SPEC-001::25]
Remote clients may observe and, where permitted, supervise sequence execution.

The platform shall distinguish:
- remote observation only
- remote launch authority
- remote pause/resume authority
- remote abort authority
- remote parameter override authority

All remote sequence actions shall be attributed and logged.

## 26. Multi-Client Expectations [SEC:UDQ-SEQ-SPEC-001::26]
Multiple clients may observe the same sequence instance.

Where multiple clients possess control rights, the platform shall make clear:
- who last issued a control action
- what control action is pending or in force
- whether a local client is view-only due to another active supervisory context

Frontend disagreement shall not create multiple truths about the same sequence state.

## 27. Anti-Patterns [SEC:UDQ-SEQ-SPEC-001::27]
The platform shall avoid the following:
- frontend-only sequence truth
- hidden step transitions
- opaque failure states without causal detail
- direct hardware writes that bypass output arbitration
- silent continuation after interlock/safe-state events
- simulated sequence runs that resemble live runs without distinction
- arbitrary code execution disguised as sequence authoring
- sequence revisions silently altering active runtime instances

## 28. Implementation Phasing Guidance [SEC:UDQ-SEQ-SPEC-001::28]
A sensible phasing path is:

## Phase 1
- structured linear sequences
- waits, prompts, command steps, verification, timeouts
- start/stop/pause/abort
- runtime preview and event logging

## Phase 2
- branching
- subsequences
- reusable parameters
- stronger evidence capture
- improved recovery and review tools

## Phase 3
- richer workflow constructs
- approval gates
- limited advanced templating
- carefully bounded persistent resumption models if justified

Phasing shall not change the canonical model in incompatible ways without controlled revision.

## 29. Requirement-Grade Statements [SEC:UDQ-SEQ-SPEC-001::29]
- Sequences shall be backend-owned structured execution objects.
- Sequence-originated actions shall enter the canonical output arbitration framework as requests.
- Sequence state and step state shall be explicit, visible, and explainable.
- Pause, hold, resume, abort, timeout, and fault semantics shall be distinct.
- Sequence execution shall integrate with historian/event/audit evidence.
- Running instances shall remain bound to the revision from which they were launched unless an explicit migration model is defined.
- UI surfaces shall support strong supervision and post-run review rather than only launch controls.
- Remote supervision, where allowed, shall be attributable and subordinate to backend authority.

## 30. Open Items for Future Detailed Docs [SEC:UDQ-SEQ-SPEC-001::30]
This specification should later feed more detailed subordinate documents for:
- exact sequence schema/config model
- sequence editor page specification
- runtime supervision page specification
- evidence capture profiles
- workflow templates and approval models
- resumable runtime persistence, if pursued
