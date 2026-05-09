---
document_id: UDQ-OUT-SPEC-001
title: Outputs, Command Arbitration, and Safe-State Specification
revision: r1
status: WIP
document_class: subsystem_spec
owner: UniversalDAQ
supersedes:
  - UDQ-OUT-SPEC-001__Outputs_Command_Arbitration_and_Safe_State_Specification__r0__WIP.md
---

# Outputs, Command Arbitration, and Safe-State Specification [SEC:UDQ-OUT-SPEC-001::0]

## Revision History [SEC:UDQ-OUT-SPEC-001::0.1]
- r1: Machine-readable normalization pass, unique section anchors, metadata cleanup, and content polish against the current governed corpus.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-OUT-SPEC-001::1]

This document defines the canonical model and governing behavior for:
- output-capable points,
- command requests,
- command ownership and arbitration,
- safe-state doctrine,
- blocked/inhibited behavior,
- output execution traceability,
- interactions with signals, rules, sequences, devices, UI clients, remote clients, and protocols.

The goal is to ensure that UniversalDAQ can support supervisory control and device actuation without ambiguity about who requested an output, who currently owns it, whether it is allowed, and what happens when the system degrades or faults.

This document does **not** define protocol-specific details such as Modbus register maps. Protocol specifics shall be defined in downstream integration specifications and shall conform to this output model.

---

## 2. Scope [SEC:UDQ-OUT-SPEC-001::2]

This specification applies to all commandable or writable points in UniversalDAQ, including but not limited to:
- digital outputs,
- analog outputs,
- writable virtual outputs,
- protocol-backed writable points,
- device commands represented as named actions,
- sequence-start/stop/reset commands,
- supervisory setpoint requests,
- controlled mode-selection requests,
- future output-capable abstractions introduced by plugins or protocol adapters.

The specification covers both local and remote command requests.

---

## 3. Core Doctrine [SEC:UDQ-OUT-SPEC-001::3]

### 3.1 Backend Authority [SEC:UDQ-OUT-SPEC-001::3.1]
All output requests shall be submitted to a backend-authoritative arbitration layer. No frontend, remote client, rules editor, or sequence view shall be treated as the final source of truth for an output’s authoritative state.

### 3.2 Requests vs Applied State [SEC:UDQ-OUT-SPEC-001::3.2]
A request to change an output is not the same thing as the output being applied. UniversalDAQ shall distinguish at minimum:
- requested state/value,
- arbitration result,
- pending/application-in-progress state,
- applied/confirmed state where confirmability exists,
- blocked/denied/inhibited state,
- safe-forced state.

### 3.3 Named Output Model [SEC:UDQ-OUT-SPEC-001::3.3]
Users should normally interact with named logical outputs or named commands, not raw device primitives. Hardware-specific identifiers may exist in advanced/service views but shall not be the primary operator-facing abstraction.

### 3.4 Safe by Default [SEC:UDQ-OUT-SPEC-001::3.4]
If command authority, communications, validity, or permissive state is uncertain, the platform shall resolve behavior according to explicit safe-state doctrine rather than silent best-guess continuation.

### 3.5 Full Explainability [SEC:UDQ-OUT-SPEC-001::3.5]
For every output-capable point, the platform shall be able to explain:
- current owner,
- current requested value,
- current applied value if known,
- source of the winning request,
- reasons lower-priority requests were not applied,
- active interlocks/permissives/inhibits,
- whether safe-state or degraded-state logic is in effect,
- timestamps of last request and last state transition.

---

## 4. Canonical Output Object [SEC:UDQ-OUT-SPEC-001::4]

Every output-capable point shall be represented by a canonical output object with stable identity independent of UI labels.

### 4.1 Required Core Fields [SEC:UDQ-OUT-SPEC-001::4.1]
At minimum, the canonical object shall include:
- stable output ID,
- human-readable name,
- display label,
- type,
- subtype/capability class,
- device binding or virtual binding,
- units where applicable,
- value domain or allowable state set,
- normal/default state,
- configured safe state/value,
- quality/availability status,
- writable capability status,
- confirmation capability,
- ownership/arbitration state,
- enable/disable state,
- audit metadata.

### 4.2 Output Type Classes [SEC:UDQ-OUT-SPEC-001::4.2]
The model shall support at minimum:
- boolean outputs,
- enumerated outputs,
- numeric analog outputs,
- pulse/momentary outputs,
- named command outputs,
- virtual output targets,
- grouped or compound outputs where one logical command affects multiple low-level writes.

### 4.3 Capability Metadata [SEC:UDQ-OUT-SPEC-001::4.3]
Each output shall expose capabilities such as:
- readback available / not available,
- write confirmation available / inferred only,
- supports ramping or slew limiting,
- supports pulse semantics,
- supports hold-last-value,
- supports local manual control,
- supports sequence control,
- supports rule-driven control,
- supports remote control,
- supports safe-force behavior,
- supports acknowledgment/reset semantics where relevant.

---

## 5. Command Request Model [SEC:UDQ-OUT-SPEC-001::5]

### 5.1 Canonical Command Request [SEC:UDQ-OUT-SPEC-001::5.1]
Every output-affecting action shall become a canonical command request object. A request shall at minimum include:
- request ID,
- timestamp,
- origin class,
- origin instance identity,
- target output ID,
- requested operation,
- requested value/state,
- request mode,
- optional duration or timing metadata,
- optional note/reason,
- correlation/reference to rule/sequence/user action where applicable.

### 5.2 Origin Classes [SEC:UDQ-OUT-SPEC-001::5.2]
At minimum, origin classes shall include:
- local operator UI,
- local engineering/service UI,
- remote supervisory client,
- rule engine,
- sequence engine,
- startup/restore logic,
- safe-state manager,
- device adapter internal recovery logic where allowed,
- test/simulation subsystem.

### 5.3 Request Operations [SEC:UDQ-OUT-SPEC-001::5.3]
Supported operations shall include as applicable:
- set boolean on/off,
- set enumerated state,
- set numeric value,
- pulse,
- hold/unhold,
- start/stop/reset command,
- enter/exit mode request,
- safe-force,
- release-to-default,
- acknowledge/clear where output objects support such semantics.

### 5.4 Request Modes [SEC:UDQ-OUT-SPEC-001::5.4]
The request model shall distinguish between at least:
- supervisory request,
- manual request,
- automatic rule request,
- sequence request,
- safe-state request,
- restoration request,
- test/simulation request.

---

## 6. Ownership and Arbitration Doctrine [SEC:UDQ-OUT-SPEC-001::6]

### 6.1 One Authoritative Winner [SEC:UDQ-OUT-SPEC-001::6.1]
For any output at any given moment, there shall be at most one authoritative winning request or safe-state resolution governing the commanded state.

### 6.2 Visible Ownership [SEC:UDQ-OUT-SPEC-001::6.2]
The currently governing source shall be visible to users and diagnostics. Ownership shall not be hidden behind unexplained value changes.

### 6.3 Arbitration is a First-Class Layer [SEC:UDQ-OUT-SPEC-001::6.3]
Arbitration shall be explicit, inspectable, testable, and logged. It shall not be implicit inside random device adapters or UI event handlers.

### 6.4 Suggested Precedence Doctrine [SEC:UDQ-OUT-SPEC-001::6.4]
Unless a more specific subsystem standard overrides it, the governing precedence should be:
1. hard safe-state / emergency inhibit,
2. explicit interlock-enforced override,
3. controlled manual authority where enabled,
4. active sequence authority,
5. automatic rule authority,
6. restore/default/background behavior.

Protocol-specific write paths shall not bypass this ordering.

### 6.5 Mode-Conditioned Ownership [SEC:UDQ-OUT-SPEC-001::6.5]
Ownership may depend on system mode. For example, manual authority may only be possible in an operator-enabled manual mode, while rule authority may only be active in automatic mode. Such gating shall be explicit and visible.

### 6.6 Multi-Client Neutrality [SEC:UDQ-OUT-SPEC-001::6.6]
Remote clients and local clients shall both participate through the same backend arbitration model. Remote origin shall not be a shortcut around platform rules.

---

## 7. Interlocks, Permissives, Inhibits, and Blocks [SEC:UDQ-OUT-SPEC-001::7]

### 7.1 Separate Concepts [SEC:UDQ-OUT-SPEC-001::7.1]
The platform shall distinguish:
- **permissives**: conditions that must be true before a command may be allowed,
- **interlocks**: conditions that actively prevent or force a state,
- **inhibits**: administrative or service lockouts,
- **availability blocks**: unavailable device/protocol/output capability states,
- **quality blocks**: invalid/stale/unknown signal-based prohibitions.

### 7.2 Explainability Requirement [SEC:UDQ-OUT-SPEC-001::7.2]
When a request is denied, held, or forced away from the requested value, the platform shall surface the specific blocking reasons.

### 7.3 No Silent Suppression [SEC:UDQ-OUT-SPEC-001::7.3]
An output shall not quietly fail to respond to a command without the system marking that request as denied, blocked, pending, unavailable, or faulted.

### 7.4 Rule and Sequence Interaction [SEC:UDQ-OUT-SPEC-001::7.4]
Rules and sequences may generate requests, but permissives/interlocks/inhibits shall still be enforced at arbitration/application time.

---

## 8. Safe-State Doctrine [SEC:UDQ-OUT-SPEC-001::8]

### 8.1 Safe-State is Explicit [SEC:UDQ-OUT-SPEC-001::8.1]
Every output-capable point shall have an explicit safe-state policy. “Safe” may vary by output and device class and must not be assumed to mean simply “off.”

### 8.2 Safe-State Policy Options [SEC:UDQ-OUT-SPEC-001::8.2]
At minimum, the model shall support policies such as:
- force off,
- force on,
- force to fixed numeric value,
- force to bounded fallback value,
- release to device-native safe default,
- hold last good value for bounded time then transition,
- no autonomous forcing allowed, raise fault only.

### 8.3 Safe-State Triggers [SEC:UDQ-OUT-SPEC-001::8.3]
Safe-state entry may be triggered by configured conditions such as:
- backend shutdown,
- frontend disconnect not relevant by itself unless it affects authority policy,
- device communication loss,
- output driver failure,
- watchdog timeout,
- interlock trip,
- explicit operator safe action,
- sequence abort,
- rule-engine invalidity if configured,
- protocol/session loss for remote-controlled deployments.

### 8.4 Entry and Exit Traceability [SEC:UDQ-OUT-SPEC-001::8.4]
The system shall record when an output enters and exits safe-state, why, and what value/state was commanded.

### 8.5 Safe-State Release Rules [SEC:UDQ-OUT-SPEC-001::8.5]
Exiting safe-state shall require explicit doctrine. Depending on configuration, release may require:
- auto-clear when conditions recover,
- manual acknowledgment,
- manual recommission of output authority,
- sequence restart,
- profile/reconnect validation.

Silent re-entry to active control after a safety-related force shall be avoided unless explicitly justified by configuration and review.

---

## 9. Applied State, Readback, and Confirmation [SEC:UDQ-OUT-SPEC-001::9]

### 9.1 Distinguish Command vs Observed State [SEC:UDQ-OUT-SPEC-001::9.1]
Where readback exists, the platform shall distinguish between commanded state and observed state.

### 9.2 Confirmation Classes [SEC:UDQ-OUT-SPEC-001::9.2]
Each output shall declare a confirmation class, such as:
- no confirmation available,
- inferred confirmation from write success only,
- logical readback available,
- physical/telemetry readback available.

### 9.3 Mismatch Handling [SEC:UDQ-OUT-SPEC-001::9.3]
If commanded and observed states diverge beyond configured tolerance or duration, the platform shall surface mismatch state and emit appropriate diagnostics/events.

### 9.4 Pending State [SEC:UDQ-OUT-SPEC-001::9.4]
For commands that take time to apply, the output model shall support explicit pending/transitional states.

---

## 10. Numeric Output Semantics [SEC:UDQ-OUT-SPEC-001::10]

### 10.1 Bounded Domain [SEC:UDQ-OUT-SPEC-001::10.1]
Numeric outputs shall have explicit min/max ranges, units, and resolution expectations.

### 10.2 Optional Transform Features [SEC:UDQ-OUT-SPEC-001::10.2]
Where configured and supported, numeric outputs may support:
- clamp limits,
- inversion,
- deadband,
- rate/slew limits,
- ramping,
- fallback value,
- safe startup/shutdown values,
- source binding to a signal or derived value under arbitration control.

### 10.3 Request Validation [SEC:UDQ-OUT-SPEC-001::10.3]
Requests outside allowed bounds shall not be silently applied. They shall be rejected, clamped according to explicit policy, or transformed according to configured doctrine, and the resulting behavior shall be visible.

---

## 11. Boolean and Pulse Output Semantics [SEC:UDQ-OUT-SPEC-001::11]

### 11.1 Boolean Clarity [SEC:UDQ-OUT-SPEC-001::11.1]
Boolean outputs shall distinguish requested ON/OFF state, actual state if known, and forced/blocked condition.

### 11.2 Pulse/Momentary Semantics [SEC:UDQ-OUT-SPEC-001::11.2]
Pulse operations shall define:
- pulse width,
- retrigger behavior,
- minimum off time,
- allowable origins,
- what happens if blocked mid-request,
- whether confirmation is required.

### 11.3 Latching Behavior [SEC:UDQ-OUT-SPEC-001::11.3]
Where latching or held commands exist, latch semantics shall be explicit and visible.

---

## 12. Restore, Startup, and Shutdown Behavior [SEC:UDQ-OUT-SPEC-001::12]

### 12.1 Restore is Not Blind Reapplication [SEC:UDQ-OUT-SPEC-001::12.1]
Restoring UI state or session state shall not imply blind restoration of output commands.

### 12.2 Startup Output Policy [SEC:UDQ-OUT-SPEC-001::12.2]
The platform shall define startup output behavior, at minimum supporting distinctions between:
- do not assert outputs until validated,
- initialize to configured safe startup values,
- restore bounded prior values only for approved outputs,
- require explicit operator re-enable.

### 12.3 Shutdown Policy [SEC:UDQ-OUT-SPEC-001::12.3]
Shutdown behavior shall include orderly output handling. Where required, outputs shall transition to configured shutdown/safe values and the result shall be logged.

### 12.4 Reconnect Policy [SEC:UDQ-OUT-SPEC-001::12.4]
After device reconnect or backend recovery, the platform shall explicitly reconcile:
- last requested state,
- actual device state if discoverable,
- output ownership,
- safe-state/inhibit status,
- whether reissue is allowed.

---

## 13. UI Obligations [SEC:UDQ-OUT-SPEC-001::13]

### 13.1 Output Workspace Responsibilities [SEC:UDQ-OUT-SPEC-001::13.1]
The UI shall expose output-capable objects with sufficient visibility for:
- current requested value,
- current owner,
- current availability,
- pending state,
- active blocks/inhibits,
- safe-state status,
- readback mismatch where applicable,
- auditable recent history.

### 13.2 Manual Control Responsibility [SEC:UDQ-OUT-SPEC-001::13.2]
Manual-control surfaces shall clearly indicate:
- whether manual authority is available,
- whether manual control is currently active,
- what other sources are requesting the same output,
- whether the request was accepted or blocked,
- what safe-state consequences apply.

### 13.3 No Ambiguous Controls [SEC:UDQ-OUT-SPEC-001::13.3]
The UI shall not present controls that appear live and actionable when backend authority, permissions, or output availability make them inactive, except if explicitly shown in disabled/blocked state.

### 13.4 Live Trace Requirement [SEC:UDQ-OUT-SPEC-001::13.4]
Users shall be able to inspect why an output is in its current state and which entity owns it.

---

## 14. Interaction with Rules, Sequences, and Signals [SEC:UDQ-OUT-SPEC-001::14]

### 14.1 Rules Generate Requests [SEC:UDQ-OUT-SPEC-001::14.1]
Rules shall generate output requests, not direct hardware writes.

### 14.2 Sequences Generate Requests [SEC:UDQ-OUT-SPEC-001::14.2]
Sequences shall generate time-ordered requests and state transitions, not bypass arbitration.

### 14.3 Signals Gate Outputs [SEC:UDQ-OUT-SPEC-001::14.3]
Signals and derived signals may participate in permissives, interlocks, safe-state triggers, and rule conditions. Their quality state shall matter in output eligibility.

### 14.4 Quality-Aware Gating [SEC:UDQ-OUT-SPEC-001::14.4]
If configured gating signals are stale, invalid, or indeterminate, the resulting eligibility of an output request shall follow explicit policy rather than silent optimistic assumption.

---

## 15. Eventing, Historian, and Audit [SEC:UDQ-OUT-SPEC-001::15]

### 15.1 Output Event Requirements [SEC:UDQ-OUT-SPEC-001::15.1]
The system shall record output-related events such as:
- request submitted,
- request won/lost arbitration,
- request blocked/denied,
- value applied,
- mismatch detected,
- safe-state entered/exited,
- ownership changed,
- inhibit/interlock trip/clear,
- manual authority entered/exited.

### 15.2 Historian Separation [SEC:UDQ-OUT-SPEC-001::15.2]
Historian storage of output values should distinguish where possible between:
- requested state/value,
- applied/observed state/value,
- ownership state,
- quality/availability state.

### 15.3 Audit Traceability [SEC:UDQ-OUT-SPEC-001::15.3]
Every significant output change shall be attributable to a source and time.

---

## 16. Remote Supervision Implications [SEC:UDQ-OUT-SPEC-001::16]

### 16.1 Remote is Policy-Bounded [SEC:UDQ-OUT-SPEC-001::16.1]
Remote command participation shall be controlled by deployment policy and shall not be assumed universally permitted.

### 16.2 Attribution [SEC:UDQ-OUT-SPEC-001::16.2]
Remote-origin requests shall include client/session attribution.

### 16.3 Remote Blocking Visibility [SEC:UDQ-OUT-SPEC-001::16.3]
If remote supervision is view-only or partially restricted, the platform shall make that explicit rather than presenting apparently operable controls that cannot succeed.

---

## 17. Validation and Testing Requirements [SEC:UDQ-OUT-SPEC-001::17]

The output/arbitration subsystem shall be testable against scenarios including at minimum:
- competing requests from different origin classes,
- manual vs sequence conflict,
- rule vs safe-state conflict,
- stale/invalid gating signals,
- reconnect after device loss,
- pending command timeout,
- command/readback mismatch,
- startup and shutdown transitions,
- pulse outputs under block conditions,
- remote request attribution and restriction,
- restore behavior after restart.

A diagnostic harness shall be able to report output capabilities, arbitration state, ownership transitions, and blocked reasons in a field-usable way.

---

## 18. Anti-Patterns [SEC:UDQ-OUT-SPEC-001::18]

The following are explicitly disallowed:
- frontend-direct output writes that bypass arbitration,
- silent clamping or rejection with no visibility,
- hidden ownership changes,
- reusing the same field to mean both requested and applied value,
- assuming “safe” always means “off,”
- automatic resume of prior control after safety-related interruption without explicit policy,
- ambiguous controls during disconnected/unavailable states,
- rules or sequences directly mutating hardware state outside the output manager.

---

## 19. Downstream Specification Obligations [SEC:UDQ-OUT-SPEC-001::19]

This specification shall be used as an input to at minimum:
- Modbus Integration Specification,
- UI workspace/page specifications for outputs and live trace,
- Requirements Traceability Matrix updates,
- Definition of Complete by Subsystem updates,
- proof/audit criteria related to command authority and safe-state behavior.
