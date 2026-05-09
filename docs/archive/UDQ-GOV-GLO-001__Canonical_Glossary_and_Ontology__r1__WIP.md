---
document_id: UDQ-GOV-GLO-001
title: Canonical Glossary and Ontology
revision: r1
status: WIP
document_class: glossary
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-STD-002
  - UDQ-GOV-SPEC-002
revision_history:
  - "r1 | 2026-03-21 | Expanded the glossary into an operational semantic backbone for contradiction control, duplication control, and future implementation handoff."
  - "r0 | 2026-03-21 | Establishes canonical project vocabulary and high-level ontology anchors."
---
# Canonical Glossary and Ontology {#gov-glo-001.s01}

## 1. Purpose [SEC:UDQ-GOV-GLO-001::1]

This document defines the canonical meaning of core UniversalDAQ terms so that architecture, subsystem specifications, UI specifications, reports, templates, registries, and future code artifacts use the same vocabulary.

## 2. Governing semantic rule [SEC:UDQ-GOV-GLO-001::2]

This glossary is the owning definition source for the terms listed here unless a higher-precedence governance document explicitly states otherwise. Subordinate documents may narrow a term for a subsystem context, but they shall not silently redefine the term.

## 3. Core ontology anchors [SEC:UDQ-GOV-GLO-001::3]

- A **device** is an addressable integration object with identity, capabilities, health, and one or more exposed points.
- A **signal** is a named data object with stable identity, type, quality state, timestamp, and value semantics.
- A **derived signal** is a signal computed from one or more other signals through governed logic.
- An **output** is a commandable target whose requested, applied, and observed states may differ.
- A **rule** is a governed condition-to-action definition that produces a request rather than an uncontrolled write.
- A **sequence** is a governed execution definition composed of steps and runtime state.
- An **event** is a discrete historical occurrence.
- An **alarm** is an event-bearing abnormal condition that may require acknowledgment or operator attention.
- A **profile** is a persisted user/session configuration bundle.
- A **workspace** is a major UI operating surface with a defined purpose.

## 4. Authority and command terms [SEC:UDQ-GOV-GLO-001::4]

### 4.1 Output request [SEC:UDQ-GOV-GLO-001::4.1]
A command intent issued by a user, rule, sequence, remote surface, or automatic safety path for later arbitration and authorization. A request is not proof that the command was accepted or applied.

### 4.2 Requested state [SEC:UDQ-GOV-GLO-001::4.2]
The state/value implied by the current accepted or pending request record. Requested state may be visible before applied state exists, but it shall never be visually conflated with applied or observed state.

### 4.3 Applied state [SEC:UDQ-GOV-GLO-001::4.3]
The backend-published state that the platform believes it has actually sent or committed after arbitration, capability checks, and authorization.

### 4.4 Observed state [SEC:UDQ-GOV-GLO-001::4.4]
A measured, inferred, or device-reported state used to confirm actual behavior after an output request. Observed state is downstream evidence, not merely a prettier name for applied state.

### 4.5 Ownership [SEC:UDQ-GOV-GLO-001::4.5]
The currently governing source or mode that has the right to influence a commandable target. Ownership is runtime truth published by the backend, not a UI guess.

### 4.6 Arbitration [SEC:UDQ-GOV-GLO-001::4.6]
The governed backend process that resolves competing requests, authority boundaries, permissives, interlocks, safe-state policy, and capability constraints into a bounded outcome.

### 4.7 Manual [SEC:UDQ-GOV-GLO-001::4.7]
A human-origin command path that is distinct from automated rule, sequence, remote, or safe-state origin. Manual means origin and mode, not automatic superiority.

### 4.8 Remote [SEC:UDQ-GOV-GLO-001::4.8]
A client or supervision surface that is not the local primary UI surface. Remote capability is deployment-bounded and shall not be assumed to equal local capability.

### 4.9 Safe state [SEC:UDQ-GOV-GLO-001::4.9]
The explicit state a subsystem or output must assume when risk, loss of health, or authority policy requires a controlled fallback.

## 5. Runtime quality and state terms [SEC:UDQ-GOV-GLO-001::5]

### 5.1 Quality state [SEC:UDQ-GOV-GLO-001::5.1]
A classification that expresses whether a value is good, stale, invalid, disconnected, simulated, blocked, or otherwise degraded.

### 5.2 Live [SEC:UDQ-GOV-GLO-001::5.2]
Presented as current runtime truth with active freshness assumptions and current backend authority. Live does not mean merely most recent cached value.

### 5.3 Historical [SEC:UDQ-GOV-GLO-001::5.3]
Presented from recorded evidence rather than current authoritative runtime publication.

### 5.4 Review mode [SEC:UDQ-GOV-GLO-001::5.4]
A UI posture in which the user is intentionally exploring historical or evidence-oriented material rather than simply following live runtime operation.

### 5.5 Live trace [SEC:UDQ-GOV-GLO-001::5.5]
An explainability surface showing current reasoning or causal chain across signals, conditions, rules, actions, ownership, or command outcomes while the system remains in live runtime posture.

### 5.6 Stale [SEC:UDQ-GOV-GLO-001::5.6]
Value freshness has exceeded declared limits but the last known value remains visible for context.

### 5.7 Invalid [SEC:UDQ-GOV-GLO-001::5.7]
A value is present but cannot be trusted because it fails validation, range, decode, integrity, or other governing checks.

### 5.8 Disconnected [SEC:UDQ-GOV-GLO-001::5.8]
The source path needed to acquire current truth is unavailable or no longer communicative.

### 5.9 Degraded [SEC:UDQ-GOV-GLO-001::5.9]
A broader health or quality condition indicating partial loss of capability, fidelity, or timeliness while some operation continues.

### 5.10 Simulated [SEC:UDQ-GOV-GLO-001::5.10]
Generated or injected for test, demonstration, or substitution purposes rather than representing ordinary live physical acquisition.

### 5.11 Blocked [SEC:UDQ-GOV-GLO-001::5.11]
A request or runtime path is currently prevented from proceeding because a governing condition, authority state, interlock, or policy constraint is active.

### 5.12 Pending [SEC:UDQ-GOV-GLO-001::5.12]
A request or transition has been issued or accepted but is not yet complete.

## 6. Protection and control terms [SEC:UDQ-GOV-GLO-001::6]

### 6.1 Interlock [SEC:UDQ-GOV-GLO-001::6.1]
A hard blocking condition that prevents a request from being applied while the blocking condition is active.

### 6.2 Permissive [SEC:UDQ-GOV-GLO-001::6.2]
A required enabling condition that must be true before an action may proceed.

### 6.3 Inhibit [SEC:UDQ-GOV-GLO-001::6.3]
A deliberate suppression or block applied by policy, state, or operator/service mode.

## 7. Event and evidence terms [SEC:UDQ-GOV-GLO-001::7]

### 7.1 Event [SEC:UDQ-GOV-GLO-001::7.1]
A discrete historical occurrence that can be recorded with time, origin, context, and evidence relationship.

### 7.2 Alarm [SEC:UDQ-GOV-GLO-001::7.2]
An event-bearing abnormal condition that may require operator attention, acknowledgment, latching behavior, shelving, suppression, or return-to-normal handling.

### 7.3 Acknowledgment [SEC:UDQ-GOV-GLO-001::7.3]
A recorded user action indicating recognition of an alarm or event state without erasing historical truth.

### 7.4 Review bundle [SEC:UDQ-GOV-GLO-001::7.4]
A governed export artifact set containing evidence, provenance, and context for later review.

## 8. Persistence and session terms [SEC:UDQ-GOV-GLO-001::8]

### 8.1 Profile [SEC:UDQ-GOV-GLO-001::8.1]
A persisted bundle of configuration, workspace arrangement, or user/session settings. A profile may influence future behavior, but loading a profile is not identical to reasserting live machine state.

### 8.2 Autosave [SEC:UDQ-GOV-GLO-001::8.2]
A bounded persistence mechanism intended to reduce loss of local edits, layout, or review context. Autosave is not a hidden operational apply path.

### 8.3 Restore [SEC:UDQ-GOV-GLO-001::8.3]
Reconstruction of saved local/session context or governed configuration into the current application session. Restore shall be distinguished from live revalidation and from actual runtime machine state.

### 8.4 Workspace state [SEC:UDQ-GOV-GLO-001::8.4]
The state of the UI operating surface, including mode, dock layout, selection context, local edits, and review posture.

### 8.5 Machine state [SEC:UDQ-GOV-GLO-001::8.5]
Authoritative runtime state of devices, signals, outputs, ownership, alarms, and other backend-governed operational objects.

## 9. Usage guardrails [SEC:UDQ-GOV-GLO-001::9]

- A subordinate document shall not use **applied**, **observed**, **live**, **historical**, **restore**, **profile**, **interlock**, or **permissive** in a way that contradicts this glossary.
- The phrase **state restored** shall not be used where **workspace state restored** or **profile restored** is the truthful meaning.
- The phrase **live value** shall not be used for merely cached or last-known values unless freshness semantics still satisfy the live definition.
- The phrase **command succeeded** shall not be used when only a request submission is known.

## 10. Conflations explicitly prohibited [SEC:UDQ-GOV-GLO-001::10]

The following conflations are not allowed in controlled documents:

- requested state with applied state
- applied state with observed state
- restore with operational reapply
- workspace state with machine state
- live trace with historical review
- remote capability with local parity
- acknowledgment with historical erasure
