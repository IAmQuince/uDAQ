---
document_id: UDQ-ARCH-NAR-002
title: Platform Controls Narrative
revision: r4
status: WIP
classification:
  domain: ARCH
  type: NAR
  sequence: '002'
effective_date: '2026-03-24'
authoring_context: UniversalDAQ
depends_on:
- UDQ-ARCH-NAR-001
- UDQ-GOV-STD-001
- UDQ-UI-ARCH-001
- UDQ-UI-MOD-001
- UDQ-UI-NAR-001
supersedes:
- UDQ-ARCH-NAR-002__Platform_Controls_Narrative__r3__WIP.md
superseded_by: []
machine_readable_artifacts: []
---
# Platform Controls Narrative

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r4 | 2026-03-24 | WIP | Restored full controlled body after accidental truncation during cleanup; retained the current bounded runtime/event/command/orchestration doctrine note. |
| r3 | 2026-03-21 | WIP | Retrofitted to YAML front matter, stable section IDs, and the machine-readable cross-reference scheme. |
| r1 | 2026-03-21 | WIP | First controlled revision created by placing the document under the universalDAQ document control scheme and establishing formal metadata and revision history. |
| r2 | 2026-03-21 | WIP | Revised to integrate the UI foundation documents, expand frontend/backend authority doctrine, add command/ownership publication expectations, and identify UI-facing architectural responsibilities that now feed downstream subsystem specifications. |

## 1. Purpose [SEC:UDQ-ARCH-NAR-002::1]

This document defines how **UniversalDAQ itself** behaves as a control-capable software platform.

The **System Controls Narrative** defines the behavior expected of a controlled installation that uses UniversalDAQ. This document narrows the scope and defines how the platform must be structured and behave internally in order to deliver that system behavior, including the operator-facing and remote-facing consequences.

This is therefore the platform-side answer to questions such as:

- What parts of the platform own truth?
- Where are normalization, quality evaluation, derived-state evaluation, rule evaluation, command arbitration, historian writes, alarms, and remote publication performed?
- What responsibilities belong to the backend versus the frontend?
- How are stale, missing, malformed, contradictory, duplicate, or delayed data handled?
- How are commands admitted, sequenced, acknowledged, denied, retried, timed out, or failed?
- How does the platform behave during startup, runtime degradation, service loss, restore, and shutdown?
- What evidence must the platform emit so runtime behavior can be reconstructed and verified?

This document is intentionally **domain-neutral**. It does not define any particular process, machine, or facility. It defines the internal control doctrine of the platform that will later host a process-specific deployment.

---

## 2. Scope [SEC:UDQ-ARCH-NAR-002::2]

This narrative applies to the UniversalDAQ software platform as a whole, including:

- backend runtime services
- device adapters and driver-facing layers
- protocol integration layers
- signal registry and canonical data model
- quality/state evaluation logic
- derived-signal and derived-condition logic
- command and output routing logic
- alarm/event generation
- historian/event persistence
- configuration and persisted-state loading
- frontend subscriptions and operator-facing state publication
- remote viewers and remote supervisory clients
- diagnostics and health services
- startup, shutdown, recovery, and degraded-service behavior

This document does **not** replace deployment-specific cause-and-effect, device-specific behavior tables, or application-specific sequence definitions. It defines the behavior of the platform that hosts those definitions.

---

## 3. Core platform doctrine [SEC:UDQ-ARCH-NAR-002::3]

### 3.1 Backend authority [SEC:UDQ-ARCH-NAR-002::3.1]
The backend runtime is the single authoritative owner of canonical runtime truth. It owns live state synthesis, quality state, derived state, command eligibility, output ownership, arbitration, and event evidence.

### 3.2 Frontend role [SEC:UDQ-ARCH-NAR-002::3.2]
The frontend owns presentation, interaction capture, local drafting, local continuity, workspace management, and operator explanation surfaces. It does not own final control truth.

### 3.3 Remote client role [SEC:UDQ-ARCH-NAR-002::3.3]
Remote clients are additional consumers and request origins. They do not bypass backend arbitration.

### 3.4 Canonical publication [SEC:UDQ-ARCH-NAR-002::3.4]
The platform shall publish operator-facing state as canonical snapshots/events that include enough information for the UI to show value, quality, freshness, ownership, block reason, and request lifecycle honestly.

### 3.5 One-platform object model [SEC:UDQ-ARCH-NAR-002::3.5]
Devices, signals, derived signals, outputs, rules, sequences, alarms/events, and profiles shall be first-class platform objects. UI workspaces, persistence, diagnostics, and remote publication shall consume these objects rather than invent their own hidden copies of truth.

---

## 4. Major platform object families [SEC:UDQ-ARCH-NAR-002::4]

### 4.1 Devices and protocols [SEC:UDQ-ARCH-NAR-002::4.1]
Devices are concrete integrations with hardware or services. Protocols are first-class integration paths such as LabJack, serial, TCP/IP, Modbus RTU, Modbus TCP, and future pluggable interfaces.

### 4.2 Signals [SEC:UDQ-ARCH-NAR-002::4.2]
Signals are named canonical observable values, whether sourced from hardware, files, protocols, services, or derived logic. They carry engineering representation plus quality and provenance.

### 4.3 Derived signals and conditions [SEC:UDQ-ARCH-NAR-002::4.3]
Derived signals are computed values. Derived conditions are computed boolean/enumerated supervisory facts. Both must be authoritative backend objects.

### 4.4 Outputs and commandable points [SEC:UDQ-ARCH-NAR-002::4.4]
Outputs are backend-mediated commandable points including digital, analog, protocol write targets, virtual outputs, and workflow triggers.

### 4.5 Rules / conditions / actions [SEC:UDQ-ARCH-NAR-002::4.5]
The platform shall support a rule-engine direction based on canonical backend-owned representations that later support both visual authoring and function-style DSL authoring.

### 4.6 Sequences / workflows [SEC:UDQ-ARCH-NAR-002::4.6]
Sequences are structured procedural control objects distinct from low-level rule evaluation.

### 4.7 Historian / event / evidence objects [SEC:UDQ-ARCH-NAR-002::4.7]
Historian records, event records, command audit records, diagnostics, and exportable evidence are first-class products of the platform.

### 4.8 UI session/profile objects [SEC:UDQ-ARCH-NAR-002::4.8]
UI layout, workspace state, session restore information, and profiles are first-class persisted objects, but they are explicitly non-authoritative relative to live machine truth.

---

## 5. End-to-end control pipeline [SEC:UDQ-ARCH-NAR-002::5]

The platform shall implement the following conceptual flow:

1. **Acquire** raw data from device/protocol adapters.
2. **Normalize** into canonical signal representations.
3. **Evaluate quality** including freshness, validity, disconnect, simulation, and contradiction state.
4. **Compute derived signals and conditions**.
5. **Evaluate alarms, permissives, interlocks, rules, and sequence conditions**.
6. **Publish canonical state** for UI and remote consumers.
7. **Accept command requests** from local UI, remote UI, sequences, rules, or safe-state logic.
8. **Arbitrate requests** using authority, mode, ownership, and permissive/interlock logic.
9. **Apply outputs** through adapter/protocol layers where allowed.
10. **Persist evidence** for historian, eventing, diagnostics, and audit.

The frontend participates at steps 6 and 7. It does not replace steps 1 through 5 or step 8.

---

## 6. Frontend/backend contract doctrine [SEC:UDQ-ARCH-NAR-002::6]

### 6.1 Required backend publication content [SEC:UDQ-ARCH-NAR-002::6.1]
The backend shall publish enough information for the frontend to present, at minimum:

- current value/state
- timestamp/freshness state
- quality state
- provenance/source identity where relevant
- command eligibility
- current owner of commandable point
- pending request state
- blocked/denied reason where applicable
- sequence state where applicable
- alarm/event state where applicable

### 6.2 Frontend-local drafts [SEC:UDQ-ARCH-NAR-002::6.2]
The frontend may hold local draft edits for configuration, rules, sequences, layouts, and profiles. Draft state shall remain explicitly non-authoritative until validated and accepted by the backend or persisted through an approved path.

### 6.3 Restore boundaries [SEC:UDQ-ARCH-NAR-002::6.3]
The platform shall prevent UI session restore from being mistaken for runtime control restore. Layout/session continuity and machine truth are separate responsibilities.

### 6.4 Historical review boundaries [SEC:UDQ-ARCH-NAR-002::6.4]
Historical review is a legitimate frontend state but shall be distinguishable from live authoritative viewing.

---

## 7. Data quality and off-nominal handling doctrine [SEC:UDQ-ARCH-NAR-002::7]

The platform shall explicitly detect and handle:

- stale values
- malformed values
- invalid values
- duplicate values/events
- delayed values/events
- contradictory values
- disconnected device/protocol states
- simulated/test values
- partial synchronization states

These states must influence not only backend decisions but also the published UI state. Silent discard without trace is not acceptable when the condition matters to control or operator understanding.

---

## 8. Command, ownership, and arbitration doctrine [SEC:UDQ-ARCH-NAR-002::8]

### 8.1 Request admission [SEC:UDQ-ARCH-NAR-002::8.1]
All command requests shall be admitted through a common backend path regardless of origin.

### 8.2 Distinct origins [SEC:UDQ-ARCH-NAR-002::8.2]
The backend shall preserve request origin and make it available for evidence and, where relevant, UI display.

### 8.3 Ownership model [SEC:UDQ-ARCH-NAR-002::8.3]
The backend shall resolve and publish current ownership of commandable points. Ownership and blocked state shall be visible to the frontend rather than reconstructed heuristically by the UI.

### 8.4 Safe-state precedence [SEC:UDQ-ARCH-NAR-002::8.4]
Safe-state, interlock, and other top-priority safety logic shall override lower-priority requests.

### 8.5 Pending and failed requests [SEC:UDQ-ARCH-NAR-002::8.5]
The backend shall expose pending, accepted, denied, timed-out, executed, and failed request states sufficiently for UI explainability and audit.

---

## 9. UI-facing architectural consequences [SEC:UDQ-ARCH-NAR-002::9]

The new UI foundation documents imply the following platform responsibilities.

### 9.1 Graph-dominant supervision support [SEC:UDQ-ARCH-NAR-002::9.1]
The backend and historian services shall support live trends, sliding-window review, whole-session review, and return-to-live interaction patterns without ambiguous state publication.

### 9.2 Workspace support [SEC:UDQ-ARCH-NAR-002::9.2]
The object model and APIs shall support workspaces for devices, signals, outputs, rules, sequences, historian/review, events/logs, diagnostics, profiles, and remote observation/supervision.

### 9.3 Explainability support [SEC:UDQ-ARCH-NAR-002::9.3]
The platform shall provide reason paths for blocked outputs, failed commands, stale/invalid values, rule state, and sequence state to support the UI explainability doctrine.

### 9.4 Protocol-first-class support [SEC:UDQ-ARCH-NAR-002::9.4]
Protocol integrations, especially Modbus, shall be first-class in the architecture rather than bolted-on page-specific hacks.

### 9.5 Dual-mode rule-authoring direction [SEC:UDQ-ARCH-NAR-002::9.5]
The backend rule model shall be suitable for both a structured visual builder and a function-style DSL, using one canonical representation.

---

## 10. Persistence and recovery doctrine [SEC:UDQ-ARCH-NAR-002::10]

### 10.1 Platform persistence layers [SEC:UDQ-ARCH-NAR-002::10.1]
The platform shall distinguish among:

- authoritative runtime state,
- configuration state,
- evidence/history state,
- UI/session continuity state.

### 10.2 Recovery behavior [SEC:UDQ-ARCH-NAR-002::10.2]
On restart or reconnect, the platform shall reconcile these layers explicitly. Cached UI continuity shall not be allowed to overwrite authoritative runtime truth.

### 10.3 Corruption boundaries [SEC:UDQ-ARCH-NAR-002::10.3]
Corrupt or partial persisted artifacts shall lead to bounded degraded behavior and diagnostics rather than undefined silent reuse.

---

## 11. Diagnostics and evidence doctrine [SEC:UDQ-ARCH-NAR-002::11]

The platform shall produce enough diagnostics and evidence to determine:

- whether backend services are alive,
- whether devices/protocols are healthy,
- whether historian/event persistence is healthy,
- whether publication to UIs/remotes is healthy,
- which request path was used,
- why a command was blocked, denied, or failed,
- what state transition occurred and when.

These diagnostics shall support both engineering/service workflows and package-audit/release workflows.

---

## 12. Anti-patterns [SEC:UDQ-ARCH-NAR-002::12]

The following are platform anti-patterns and shall not be normalized into the architecture:

- frontend-private truth that diverges from backend truth,
- UI reconstruction of ownership using guesswork,
- raw protocol/register concepts leaked everywhere into ordinary operator workflows,
- output state changes with no audit trail,
- implicit rule semantics that cannot round-trip between representations,
- restore logic that silently reasserts stale control intent,
- protocol-specific page logic standing in for a proper platform object model.

---

## 13. Downstream document consequences [SEC:UDQ-ARCH-NAR-002::13]

This narrative now drives the following downstream documents and specs:

- Requirements Traceability Matrix
- Definition of Complete by Subsystem
- future Signals and Derived Signals Specification
- future Rules / Conditions / Actions Specification
- future Outputs / Arbitration / Safe-State Specification
- future Modbus Integration Specification
- future Sequence / Workflow Specification
- future Historian / Event / Evidence Specification
- future Remote Observation / Supervision Specification

---

## 14. Notes [SEC:UDQ-ARCH-NAR-002::14]

This revision moves the platform narrative from a mainly backend-internal control description to a fuller platform doctrine that explicitly accounts for UI truth publication, explanation, restore boundaries, and remote participation.

### Recovery and bounded proof closeout note [SEC:UDQ-ARCH-NAR-002::14.A]

This active revision was body-restored from `20260323_09_action_claims_identity` after the cleanup package reduced the platform narrative to a stub-sized summary. The current bounded package line still demonstrates the runtime spine, events/alarms spine, command-admission spine, orchestration skeleton, journals/summaries, correlation identifiers, and governed-action claim model, while remaining intentionally narrow with respect to broad hardware generalization, streaming depth, wide output depth, and rich workbench/editor completeness.
