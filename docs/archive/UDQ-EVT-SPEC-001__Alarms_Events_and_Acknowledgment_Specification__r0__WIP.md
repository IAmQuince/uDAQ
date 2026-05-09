---
document_id: UDQ-EVT-SPEC-001
title: Alarms, Events, and Acknowledgment Specification
revision: r0
status: WIP
classification:
  domain: EVT
  type: SPEC
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-GOV-STD-001
- UDQ-HIS-SPEC-001
- UDQ-OUT-SPEC-001
- UDQ-REM-SPEC-001
- UDQ-UI-MOD-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
audit_exceptions: []
---
# Alarms, Events, and Acknowledgment Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-21 | WIP | Initial issue defining alarm state semantics, event classes, acknowledgment behavior, shelving/suppression boundaries, and evidence obligations. |

# 1. Purpose [SEC:UDQ-EVT-SPEC-001::1]

This specification defines how UniversalDAQ shall represent alarms, non-alarm events, operator acknowledgments, and the evidence they generate.

# 2. Scope [SEC:UDQ-EVT-SPEC-001::2]

This specification applies to:

- alarm conditions raised from signals, derived signals, rules, devices, protocols, and sequence execution
- non-alarm events such as mode changes, command issuance, startup, reconnect, and package/audit activities when those are in runtime scope
- acknowledgment, shelving, suppression, return-to-normal, and closeout behavior
- local and remote viewing and acknowledgment workflows

# 3. Canonical concepts [SEC:UDQ-EVT-SPEC-001::3]

UniversalDAQ shall distinguish at minimum the following concepts:

- **alarm definition**: a governed condition that may transition into alarm state at runtime
- **alarm instance**: a runtime occurrence of an alarm definition becoming active
- **event record**: a time-stamped record of something notable having happened
- **acknowledgment**: an operator or authorized client affirming awareness of an alarm instance
- **return to normal**: the active condition clearing
- **closeout**: the alarm instance reaching a fully resolved terminal state when applicable
- **shelving**: temporary operator-directed removal from active annunciation without deleting the condition
- **suppression**: system-directed non-annunciation based on governed logic such as mode, maintenance state, or dependency masking

# 4. Alarm model [SEC:UDQ-EVT-SPEC-001::4]

## 4.1 Alarm classes [SEC:UDQ-EVT-SPEC-001::4.1]

Alarm definitions shall support explicit classing at minimum for:

- fault alarms
- process/state alarms
- communication alarms
- safety/permissive/interlock alarms
- sequence execution alarms
- diagnostic/watchdog alarms

## 4.2 Severity [SEC:UDQ-EVT-SPEC-001::4.2]

Alarm definitions shall declare an explicit severity. Severity shall affect visibility, annunciation expectations, and review priority, but shall not by itself imply acknowledgment or write authority.

## 4.3 Priority [SEC:UDQ-EVT-SPEC-001::4.3]

Alarm definitions may declare a priority independent of severity to support ordering, filtering, and operator focus.

## 4.4 Source linkage [SEC:UDQ-EVT-SPEC-001::4.4]

Each alarm definition shall be traceable to one or more governed sources such as:

- signal/derived signal conditions
- rule evaluation outcomes
- device or protocol health state
- command arbitration outcomes
- sequence/runtime execution state
- watchdog/diagnostic subsystems

# 5. Alarm state model [SEC:UDQ-EVT-SPEC-001::5]

## 5.1 Required alarm states [SEC:UDQ-EVT-SPEC-001::5.1]

UniversalDAQ shall represent alarm lifecycle states explicitly. At minimum the platform shall distinguish:

- normal
- active-unacknowledged
- active-acknowledged
- returned-to-normal-unacknowledged when applicable
- returned-to-normal-acknowledged/closed
- shelved
- suppressed

## 5.2 State honesty [SEC:UDQ-EVT-SPEC-001::5.2]

The UI and evidence model shall not collapse these states into a single generic indicator. Operators shall be able to tell whether the condition is still active, merely acknowledged, or fully cleared.

## 5.3 Latched versus self-resetting [SEC:UDQ-EVT-SPEC-001::5.3]

Alarm definitions shall declare whether they are self-resetting upon return to normal or require latching/explicit reset to close.

# 6. Event model [SEC:UDQ-EVT-SPEC-001::6]

## 6.1 Event classes [SEC:UDQ-EVT-SPEC-001::6.1]

The platform shall record non-alarm events for at minimum:

- startup/shutdown/restart
- backend connectivity transitions
- device/protocol connect/disconnect transitions
- mode and authority changes
- command request / block / apply / observe transitions
- rule enable/disable and evaluation anomalies
- sequence state changes
- acknowledgment/shelving/suppression actions
- audit, export, and package-related runtime actions when those are in scope

## 6.2 Event versus alarm separation [SEC:UDQ-EVT-SPEC-001::6.2]

Not every event is an alarm. The event model shall remain broader than the alarm model while still allowing direct cross-linking between related records.

# 7. Acknowledgment doctrine [SEC:UDQ-EVT-SPEC-001::7]

## 7.1 Meaning of acknowledgment [SEC:UDQ-EVT-SPEC-001::7.1]

Acknowledgment means the actor has indicated awareness of the alarm instance. It shall not, by itself, imply the condition has cleared or that the actor has corrected the underlying cause.

## 7.2 Allowed actors [SEC:UDQ-EVT-SPEC-001::7.2]

Only actors permitted by the command-authorization model may acknowledge alarms. All acknowledgments shall record actor identity, origin, time, and optional note text where provided.

## 7.3 Local and remote parity [SEC:UDQ-EVT-SPEC-001::7.3]

Local and remote acknowledgments shall follow the same backend-authoritative rules and produce equivalent evidence records. UI pathways may differ, but the state transition semantics shall not.

## 7.4 Batch acknowledgment [SEC:UDQ-EVT-SPEC-001::7.4]

Batch acknowledgment may be supported, but the evidence model shall still preserve which instances were acknowledged, by whom, and under what scope.

# 8. Shelving and suppression [SEC:UDQ-EVT-SPEC-001::8]

## 8.1 Shelving [SEC:UDQ-EVT-SPEC-001::8.1]

Shelving is an operator-directed temporary presentation control. Shelving shall:

- be time-bounded or explicitly reviewable
- preserve the underlying alarm condition and evidence trail
- never delete or rewrite prior alarm history
- be clearly visible in both runtime and review surfaces

## 8.2 Suppression [SEC:UDQ-EVT-SPEC-001::8.2]

Suppression is system-directed and shall be governed by declared logic or configuration. A suppressed alarm shall remain traceable, and the reason for suppression shall be inspectable.

## 8.3 Safety boundary [SEC:UDQ-EVT-SPEC-001::8.3]

Alarm presentation controls shall not silently defeat underlying interlocks, safe-state behavior, or evidence capture.

# 9. Relationship to outputs, rules, and sequences [SEC:UDQ-EVT-SPEC-001::9]

Alarms may arise from or influence:

- output inhibit/interlock states
- rule blocked/indeterminate outcomes
- sequence holds, aborts, or timeout states
- protocol/device communication degradation

When an alarm materially affects command application or sequence execution, that relationship shall be visible in live trace and preserved in evidence records.

# 10. UI obligations [SEC:UDQ-EVT-SPEC-001::10]

## 10.1 Required operator visibility [SEC:UDQ-EVT-SPEC-001::10.1]

The UI shall support, at minimum:

- active alarm list
- acknowledged/unacknowledged distinction
- return-to-normal visibility
- event timeline or event list review
- inspection of alarm source and contributing context
- acknowledgment/shelving actions where authorized
- filter/sort/group behavior by severity, class, source, and time

## 10.2 Explainability [SEC:UDQ-EVT-SPEC-001::10.2]

For each active or historical alarm instance, the platform should expose enough context to explain what caused it, what it affected, and how it resolved.

# 11. Historian and evidence obligations [SEC:UDQ-EVT-SPEC-001::11]

Every alarm lifecycle transition and every acknowledgment-related action shall be evidence-bearing. At minimum the historian/evidence layer shall preserve:

- alarm definition identifier
- alarm instance identifier
- event type and state transition
- timestamp and source clock context
- actor and origin where human or client action occurred
- related signal/rule/device/sequence identifiers when applicable
- freeform note text when provided

# 12. Remote and multi-client implications [SEC:UDQ-EVT-SPEC-001::12]

Remote clients may view and, where permitted, acknowledge or shelve alarms. The backend shall remain the single authority for alarm state transitions so that multiple clients do not create divergent views of the same instance.

# 13. Validation and test obligations [SEC:UDQ-EVT-SPEC-001::13]

Alarm and acknowledgment behavior shall be testable for:

- state transition correctness
- local/remote action parity
- shelving timeout and restoration behavior
- evidence completeness
- restart/reconnect continuity
- interaction with sequences, outputs, and communication failures

# 14. Anti-patterns [SEC:UDQ-EVT-SPEC-001::14]

The platform shall avoid:

- treating acknowledgment as equivalent to resolution
- hiding whether an alarm is still active
- allowing UI-local alarm state that diverges from backend truth
- deleting evidence because an alarm was shelved or suppressed
- collapsing alarm and general event streams into an untraceable undifferentiated log

