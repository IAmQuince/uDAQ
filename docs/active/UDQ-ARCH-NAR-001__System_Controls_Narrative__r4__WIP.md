---
document_id: UDQ-ARCH-NAR-001
title: System Controls Narrative
revision: r4
status: WIP
classification:
  domain: ARCH
  type: NAR
  sequence: '001'
effective_date: '2026-03-24'
authoring_context: UniversalDAQ
depends_on:
- UDQ-GOV-STD-001
- UDQ-UI-ARCH-001
- UDQ-UI-MOD-001
- UDQ-UI-NAR-001
supersedes:
- UDQ-ARCH-NAR-001__System_Controls_Narrative__r3__WIP.md
superseded_by: []
machine_readable_artifacts: []
---
# System Controls Narrative

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r4 | 2026-03-24 | WIP | Restored full controlled body after accidental truncation during cleanup; retained the bounded proof closeout note for the current package line. |
| r3 | 2026-03-21 | WIP | Retrofitted to YAML front matter, stable section IDs, and the machine-readable cross-reference scheme. |
| r1 | 2026-03-21 | WIP | First controlled revision created by placing the document under the universalDAQ document control scheme and establishing formal metadata and revision history. |
| r2 | 2026-03-21 | WIP | Revised to fold in UI doctrine, UI functional architecture, and UI state/interaction consequences so system-level control behavior explicitly includes human supervision, remote observation/supervision, and authority-visible operator interaction. |

## 1. Purpose [SEC:UDQ-ARCH-NAR-001::1]

This document defines how a system implemented with **UniversalDAQ** is controlled at the installation-behavior level.

It is intentionally **domain-agnostic**. UniversalDAQ is not an electrolyzer controller, a building automation package, a machine-specific HMI, or a one-off test stand logger. It is a general platform for acquiring inputs, evaluating deterministic logic, presenting operator information, issuing outputs, recording evidence, and moving a controlled installation between known states.

This narrative exists to define **how the full controlled installation is expected to behave before code is written or accepted**. It is the bridge between the I/O register, the cause-and-effect logic, the UI doctrine, and the eventual implementation.

This document answers the following questions:

- What classes of inputs enter the system?
- How are those inputs validated, normalized, and time-qualified?
- How are derived conditions formed from raw inputs?
- How do derived conditions influence alarms, interlocks, permissives, sequences, and outputs?
- How is manual authority separated from automatic authority?
- What role does the operator interface play in supervision, command issue, explanation, review, and recovery?
- What must happen on startup, runtime fault, shutdown, degraded operation, and loss of communication?
- What evidence must exist to prove that the runtime behavior matched the intended behavior?

This is **not** source code and it is **not** a screen mockup. It is the deterministic control description that implementation, testing, diagnostics, UI behavior, and packaging must all trace back to.

---

## 2. Scope [SEC:UDQ-ARCH-NAR-001::2]

This narrative applies to the full deployed UniversalDAQ-controlled system, including:

- physical inputs and outputs
- software-defined inputs and outputs
- derived logical states
- operator-visible states and operator commands
- automated actions
- alarm generation and acknowledgement pathways
- interlock and permissive logic
- sequencing and timed behavior
- fault handling
- degraded-mode behavior
- state persistence and restoration boundaries
- runtime evidence generation
- local supervision and remote observation/supervision behavior

This narrative does **not** define the specific details of a particular process application. Those must be instantiated by deployment-specific I/O definitions, device maps, cause-and-effect matrices, and subsystem specifications.

---

## 3. Architectural intent [SEC:UDQ-ARCH-NAR-001::3]

UniversalDAQ is intended to act as a deterministic control shell around an arbitrary monitored or controlled process.

At a high level, the system performs the following loop:

1. Acquire raw inputs from devices, services, files, buses, or operator requests.
2. Timestamp those inputs and associate them with source identity and quality metadata.
3. Validate and normalize the inputs into canonical engineering or logical values.
4. Evaluate derived conditions, health states, alarms, interlocks, permissives, and sequence conditions.
5. Publish authoritative state for operator supervision and remote observation.
6. Determine the currently allowed command space under the active system mode and authority rules.
7. Admit, reject, or delay command requests through explicit arbitration.
8. Issue outputs only when the required permissives are satisfied and no blocking interlocks are active.
9. Record events, state transitions, actions, acknowledgements, overrides, denials, and faults.
10. Present the current system state to the operator in a way that is sufficient for supervision, diagnosis, and review.
11. Preserve enough evidence to reconstruct what the system knew, what it decided, what command was requested, what was allowed, and what actually happened.

The system is therefore not merely a logger and not merely a front end. It is a controlled state machine with evidence and an explicitly bounded human supervisory surface.

---

## 4. Fundamental control principles [SEC:UDQ-ARCH-NAR-001::4]

All deployments using UniversalDAQ shall inherit the following control principles.

### 4.1 Determinism [SEC:UDQ-ARCH-NAR-001::4.1]
For any given system state and set of valid inputs, the resulting derived conditions, allowed actions, displayed authority state, and output decisions must be reproducible.

### 4.2 Explicitness [SEC:UDQ-ARCH-NAR-001::4.2]
No important control behavior is allowed to remain implicit. If a delay, timeout, latch, reset rule, fallback rule, ownership rule, acknowledgement rule, or restore rule matters, it must be stated explicitly.

### 4.3 Separation of raw data from interpreted state [SEC:UDQ-ARCH-NAR-001::4.3]
A measured value is not the same thing as the system meaning assigned to that value. UniversalDAQ must preserve both the raw signal and the interpreted condition.

### 4.4 Quality-aware control [SEC:UDQ-ARCH-NAR-001::4.4]
No input is trusted without quality context. Each input must carry enough metadata to determine whether it is fresh, valid, plausible, and authoritative.

### 4.5 Safe degradation [SEC:UDQ-ARCH-NAR-001::4.5]
When the system loses confidence in a signal, device, communications path, or authority path, it must degrade in a defined way rather than continue behaving as though nothing happened.

### 4.6 Traceability [SEC:UDQ-ARCH-NAR-001::4.6]
Every meaningful runtime behavior must be mappable to a requirement, a control statement, a matrix row, and evidence.

### 4.7 Domain neutrality [SEC:UDQ-ARCH-NAR-001::4.7]
UniversalDAQ provides control structure, not process assumptions. All application-specific meaning must be supplied by configuration and deployment-specific control definitions.

### 4.8 Backend-authoritative supervision [SEC:UDQ-ARCH-NAR-001::4.8]
The operator interface is part of the control boundary, but it is not the source of truth. Human requests may influence the system only through defined backend-admitted command paths.

### 4.9 Honest state representation [SEC:UDQ-ARCH-NAR-001::4.9]
The system must never allow live, stale, disconnected, simulated, historical, derived, pending, or faulted states to be confused with each other at the operator-facing level.

---

## 5. Control model entities [SEC:UDQ-ARCH-NAR-001::5]

The UniversalDAQ-controlled system is described in terms of the following entities.

### 5.1 Raw inputs [SEC:UDQ-ARCH-NAR-001::5.1]
Inputs are values received from the outside world. Typical categories include analog measurements, digital statuses, counters, timestamps from external systems, communication health bits, device self-reported fault states, operator-entered values, configuration selections, file/database values, and service values.

A raw input is only the reported value plus source metadata. It has not yet become a trusted system fact.

### 5.2 Normalized inputs [SEC:UDQ-ARCH-NAR-001::5.2]
A normalized input is a raw input that has been converted into its canonical representation, such as engineering units, enum state, boolean state, or timestamp-normalized form.

### 5.3 Quality state [SEC:UDQ-ARCH-NAR-001::5.3]
A quality state expresses whether a value is good, stale, invalid, disconnected, simulated, estimated, historical, or otherwise bounded in trustworthiness.

### 5.4 Derived signals and derived conditions [SEC:UDQ-ARCH-NAR-001::5.4]
Derived signals are values calculated from one or more raw or normalized inputs. Derived conditions are boolean or enumerated interpretations used for supervision, alarms, permissives, interlocks, rule evaluation, and sequencing.

### 5.5 Commands and command requests [SEC:UDQ-ARCH-NAR-001::5.5]
A command request is a human, sequence, rule, remote, or recovery-origin request for a change. A command is not effective merely because it was requested. It becomes effective only if admitted through the authority and arbitration model.

### 5.6 Outputs [SEC:UDQ-ARCH-NAR-001::5.6]
Outputs are the commanded external effects of the system, including digital outputs, analog outputs, protocol writes, virtual outputs, and workflow triggers.

### 5.7 Modes and operating contexts [SEC:UDQ-ARCH-NAR-001::5.7]
Modes describe the installation’s operating posture, such as startup, standby, run, maintenance, manual, automatic, sequence-owned, degraded, or faulted. They govern what the system is allowed to do and what the user is allowed to request.

### 5.8 Interlocks and permissives [SEC:UDQ-ARCH-NAR-001::5.8]
Interlocks block unsafe or invalid actions. Permissives define required preconditions for a requested action.

### 5.9 Sequence states [SEC:UDQ-ARCH-NAR-001::5.9]
Sequence states describe step-based or workflow-based control progression, including current step, pending transition, hold, abort, completion, and fault interaction.

### 5.10 Operator-visible state [SEC:UDQ-ARCH-NAR-001::5.10]
Operator-visible state is a first-class system entity. It includes current values, quality, ownership, command eligibility, reason paths, alarms, active sequences, and historical evidence needed to supervise the installation honestly.

---

## 6. Control pipeline [SEC:UDQ-ARCH-NAR-001::6]

The system-wide control pipeline shall be understood as:

**acquisition -> normalization -> quality evaluation -> derivation -> permissive/interlock/rule/sequence evaluation -> authority/arbitration -> output application -> evidence publication -> operator supervision/review**

The UI sits downstream of authoritative state generation for visibility and upstream of backend arbitration for command requests. It is therefore neither a passive ornament nor an independent controller.

---

## 7. Human supervision and UI consequences [SEC:UDQ-ARCH-NAR-001::7]

### 7.1 UI as part of the control boundary [SEC:UDQ-ARCH-NAR-001::7.1]
The UI is part of the controlled system boundary because it exposes state, accepts requests, supports acknowledgement, and guides recovery. The system narrative therefore must constrain what the UI may and may not imply.

### 7.2 Required operator visibility [SEC:UDQ-ARCH-NAR-001::7.2]
A controlled installation shall make the following visible where relevant:

- current live state
- state quality and freshness
- active alarms and notable events
- active interlocks and unsatisfied permissives
- current owner of each commandable output or point
- whether a request is local, remote, rule-driven, sequence-driven, manual, or safe-state-driven
- why a command is blocked or denied
- whether the operator is viewing live data, last-known data, simulated data, or historical data

### 7.3 Required operator separation [SEC:UDQ-ARCH-NAR-001::7.3]
The system shall distinguish at least the following human/system interactions:

- observation without authority
- supervision with bounded command ability
- direct manual control where allowed
- engineering/service editing and diagnostics
- remote observation
- remote supervision

### 7.4 Restore boundary [SEC:UDQ-ARCH-NAR-001::7.4]
Restoring a UI session or profile shall never be treated as restoring actual machine state. Local continuity and live authoritative truth are separate.

---

## 8. Authority and arbitration doctrine [SEC:UDQ-ARCH-NAR-001::8]

### 8.1 General rule [SEC:UDQ-ARCH-NAR-001::8.1]
No output-changing action becomes effective unless it passes through explicit authority, permissive, interlock, and arbitration logic.

### 8.2 Distinct request origins [SEC:UDQ-ARCH-NAR-001::8.2]
The system shall distinguish between at least the following origins of requests:

- local operator UI
- remote client
- sequence/workflow engine
- rule/condition/action engine
- automatic recovery or safe-state logic
- service/maintenance action

### 8.3 Visible ownership [SEC:UDQ-ARCH-NAR-001::8.3]
If an output or commandable point is owned, blocked, or overridden, that ownership or block shall be operator-visible.

### 8.4 Safe-state precedence [SEC:UDQ-ARCH-NAR-001::8.4]
Safe-state and blocking interlock logic shall take precedence over lower-authority requests.

### 8.5 Denial visibility [SEC:UDQ-ARCH-NAR-001::8.5]
Rejected, delayed, timed-out, or blocked requests shall produce reviewable evidence and operator-visible explanation.

---

## 9. Lifecycle behavior [SEC:UDQ-ARCH-NAR-001::9]

### 9.1 Startup [SEC:UDQ-ARCH-NAR-001::9.1]
On startup the system shall:

- initialize in a defined order,
- avoid presenting cached state as authoritative live truth before synchronization,
- establish device and backend health context,
- enter a bounded state if initialization is incomplete,
- expose enough status for the operator to know whether the installation is merely launching, restored locally, synchronized, degraded, or not yet ready.

### 9.2 Runtime degradation [SEC:UDQ-ARCH-NAR-001::9.2]
If devices, communications, publication paths, or historian paths degrade, the system shall continue only within declared limits and shall surface that degraded condition honestly.

### 9.3 Loss of contact [SEC:UDQ-ARCH-NAR-001::9.3]
Loss of device or backend contact shall have defined effects on quality state, command eligibility, display state, and safe behavior.

### 9.4 Shutdown [SEC:UDQ-ARCH-NAR-001::9.4]
Shutdown shall be orderly and bounded. The system shall not silently imply that UI closure alone created a safe physical state unless that outcome is actually implemented and evidenced by the backend.

### 9.5 Recovery and reconnect [SEC:UDQ-ARCH-NAR-001::9.5]
After reconnect or recovery, the system shall reconcile local UI continuity with authoritative backend truth and shall not silently reissue stale pending control intent.

---

## 10. Remote observation and supervision [SEC:UDQ-ARCH-NAR-001::10]

Remote participation is part of the system architecture and must be bounded explicitly.

### 10.1 Remote observation [SEC:UDQ-ARCH-NAR-001::10.1]
Remote observation may include live values, historical review, alarms/events, diagnostics, and status visibility.

### 10.2 Remote supervision [SEC:UDQ-ARCH-NAR-001::10.2]
Remote supervision may include bounded acknowledgements, setpoint changes, sequence starts/stops, and selected commands where allowed by deployment policy.

### 10.3 Remote direct control [SEC:UDQ-ARCH-NAR-001::10.3]
Remote direct control is higher risk and shall not be assumed by default. If supported, it must obey the same backend authority, arbitration, evidence, and visibility rules as local control.

---

## 11. Evidence doctrine [SEC:UDQ-ARCH-NAR-001::11]

For every meaningful control event, the controlled installation should preserve enough evidence to answer:

- What was the relevant input state?
- What was the input quality state?
- What derived condition or rule state existed?
- What request was made and by whom/what?
- What ownership/arbitration state existed?
- What was blocked, denied, delayed, or allowed?
- What output change occurred, if any?
- What was shown to the operator?
- What sequence or lifecycle state existed at the time?

Evidence may include historian records, event logs, alarms, command audit records, state snapshots, diagnostics, screenshots, and release/test artifacts.

---

## 12. Downstream document consequences [SEC:UDQ-ARCH-NAR-001::12]

The following controlled documents shall trace back to this narrative:

- Platform Controls Narrative
- Requirements Traceability Matrix
- Definition of Complete by Subsystem
- UI Controls Philosophy and HMI Doctrine
- UI Functional Architecture
- UI State and Interaction Model
- future subsystem specifications for signals, rules, outputs/arbitration, Modbus, sequences, historian, and remote supervision

---

## 13. Notes [SEC:UDQ-ARCH-NAR-001::13]

This revision intentionally elevates operator-facing truth, authority visibility, and restore/reconnect boundaries into the system-level doctrine. Those themes are now foundational and shall not be treated as purely frontend implementation details.

### Recovery and bounded proof closeout note [SEC:UDQ-ARCH-NAR-001::13.A]

This active revision was body-restored from `20260323_09_action_claims_identity` after the cleanup package reduced the narrative to a stub-sized summary. The current package line still claims a bounded implemented proof for live input acquisition, variable derivation, degraded/recovery semantics, alarm raise/acknowledge/clear behavior, command admission, bounded rules/sequences orchestration, append-only evidence, and governed-action claim suppression. This recovery preserves the full architectural doctrine while retaining the current bounded proof posture.
