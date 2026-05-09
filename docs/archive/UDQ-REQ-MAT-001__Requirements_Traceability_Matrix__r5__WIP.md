---
document_id: UDQ-REQ-MAT-001
title: Requirements Traceability Matrix
revision: r5
status: WIP
document_class: requirement-matrix
owner: UniversalDAQ
depends_on:
  - UDQ-ARCH-NAR-001
  - UDQ-ARCH-NAR-002
  - UDQ-QUAL-DEF-001
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-MOD-001
  - UDQ-LOG-SPEC-001
  - UDQ-SIG-SPEC-001
  - UDQ-OUT-SPEC-001
  - UDQ-PROT-SPEC-001
  - UDQ-SEQ-SPEC-001
  - UDQ-HIS-SPEC-001
  - UDQ-REM-SPEC-001
  - UDQ-EVT-SPEC-001
  - UDQ-DIAG-SPEC-001
  - UDQ-PROF-SPEC-001
  - UDQ-DEV-SPEC-001
  - UDQ-EXP-SPEC-001
  - UDQ-SEC-SPEC-001
  - UDQ-UI-SPEC-000
  - UDQ-UI-SPEC-001
  - UDQ-UI-SPEC-002
  - UDQ-UI-SPEC-003
  - UDQ-UI-SPEC-004
  - UDQ-UI-SPEC-005
  - UDQ-QUAL-SPEC-002
  - UDQ-AUD-SPEC-001
  - UDQ-AUD-SPEC-002
  - UDQ-SCM-STD-001
  - UDQ-REL-SPEC-001
  - UDQ-GOV-STD-002
  - UDQ-GOV-REG-001
  - UDQ-GOV-REG-002
  - UDQ-GOV-SOP-001
  - UDQ-IMP-PLAN-001
  - UDQ-IMP-MAP-001
revision_history:
  - "r5 | 2026-03-21 | Added hardening-sprint governance and implementation-transition requirements."
---
# Requirements Traceability Matrix [SEC:UDQ-REQ-MAT-001::0]

## 1. Purpose [SEC:UDQ-REQ-MAT-001::1]

This matrix maps requirement identifiers to governing sources, downstream subsystem specifications, proof expectations, and package-level evidence obligations.

## 2. Requirement rows [SEC:UDQ-REQ-MAT-001::2]

| Requirement ID | Requirement Statement | Primary Source(s) | Downstream Spec(s) | Verification / Proof Expectation | Package / Runtime Evidence | Status |
|---|---|---|---|---|---|---|
| UDQ-REQ-ARCH-001 | The backend shall remain the authoritative source of runtime truth, command arbitration, and applied state publication. | UDQ-ARCH-NAR-002, UDQ-OUT-SPEC-001 | UDQ-SEC-SPEC-001, UDQ-REM-SPEC-001 | architecture review, runtime trace, command ownership test | published state trace, command log, proof bundle | Open |
| UDQ-REQ-ARCH-002 | The UI shall never silently imply authority that it does not possess. | UDQ-UI-NAR-001, UDQ-UI-MOD-001 | UDQ-UI-SPEC-002, UDQ-UI-SPEC-005 | UI review, ownership-state walkthrough | screenshots, interaction trace | Open |
| UDQ-REQ-SIG-001 | Every signal shall have stable identity independent of user-facing display name. | UDQ-SIG-SPEC-001 | UDQ-DEV-SPEC-001, UDQ-PROF-SPEC-001 | rename safety test, schema inspection | signal registry export, migration test | Open |
| UDQ-REQ-SIG-002 | Derived signals shall be dependency-tracked and cycle-checked before activation. | UDQ-SIG-SPEC-001, UDQ-LOG-SPEC-001 | UDQ-UI-SPEC-003 | validation test, negative cycle case | validation report, dependency graph export | Open |
| UDQ-REQ-OUT-001 | Output actions shall be requests subject to arbitration, permissives, interlocks, and safe-state policy rather than direct uncontrolled writes. | UDQ-OUT-SPEC-001 | UDQ-SEC-SPEC-001, UDQ-REM-SPEC-001 | arbitration test, interlock block test | requested/applied/observed trace | Open |
| UDQ-REQ-OUT-002 | Requested, applied, and observed output states shall be distinguishable in runtime behavior and evidence surfaces. | UDQ-OUT-SPEC-001, UDQ-HIS-SPEC-001 | UDQ-UI-SPEC-004, UDQ-EXP-SPEC-001 | historian review, UI overlay test | event markers, historian export | Open |
| UDQ-REQ-RULE-001 | Rules shall be represented by one canonical model with equivalent visual and DSL editing views. | UDQ-LOG-SPEC-001 | UDQ-UI-SPEC-003 | roundtrip test, AST equivalence test | proof bundle with before/after representations | Open |
| UDQ-REQ-RULE-002 | Rule evaluation shall be explainable, including quality-blocked and indeterminate cases. | UDQ-LOG-SPEC-001, UDQ-DIAG-SPEC-001 | UDQ-UI-SPEC-003, UDQ-UI-SPEC-004 | truth-trace review, blocked-case test | live trace screenshots, diagnostics export | Open |
| UDQ-REQ-MOD-001 | Modbus integration shall support TCP and RTU client modes with explicit decode, ordering, scaling, timeout, and health semantics. | UDQ-PROT-SPEC-001 | UDQ-DEV-SPEC-001, UDQ-DIAG-SPEC-001 | protocol simulation, decode tests | device config export, comms diagnostics | Open |
| UDQ-REQ-MOD-002 | Modbus-backed writable points shall participate in the same arbitration and authorization model as other outputs. | UDQ-PROT-SPEC-001, UDQ-OUT-SPEC-001 | UDQ-SEC-SPEC-001, UDQ-REM-SPEC-001 | write authorization test, arbitration conflict test | command log, permission trace | Open |
| UDQ-REQ-SEQ-001 | Sequences shall distinguish definition, revision, runtime instance, and execution state. | UDQ-SEQ-SPEC-001 | UDQ-HIS-SPEC-001, UDQ-EXP-SPEC-001 | sequence lifecycle test | sequence event history, export bundle | Open |
| UDQ-REQ-SEQ-002 | Sequence pause, hold, resume, timeout, abort, and recovery behavior shall be explicit and evidence-producing. | UDQ-SEQ-SPEC-001 | UDQ-EVT-SPEC-001, UDQ-HIS-SPEC-001 | sequence abnormal-path test | event log, state-transition timeline | Open |
| UDQ-REQ-HIS-001 | Historian data and event evidence shall preserve context linking runtime values, commands, alarms, rules, sequences, and diagnostics. | UDQ-HIS-SPEC-001 | UDQ-EXP-SPEC-001, UDQ-PROOF-TPL-001 | evidence-chain inspection | evidence bundle, historian export | Open |
| UDQ-REQ-HIS-002 | Live and historical review modes shall remain distinct and reversible without losing operator clarity. | UDQ-HIS-SPEC-001, UDQ-UI-MOD-001 | UDQ-UI-SPEC-004 | graph mode transition test | review screenshots, interaction capture | Open |
| UDQ-REQ-REM-001 | Remote surfaces shall distinguish observation, supervision, and direct control capabilities, with backend-enforced boundaries. | UDQ-REM-SPEC-001, UDQ-SEC-SPEC-001 | UDQ-UI-SPEC-005 | role-based access test | remote session audit trail | Open |
| UDQ-REQ-REM-002 | Remote-issued commands shall be attributable and visible as remote-origin actions in local and remote evidence surfaces. | UDQ-REM-SPEC-001, UDQ-HIS-SPEC-001 | UDQ-UI-SPEC-005, UDQ-EXP-SPEC-001 | multi-client attribution test | command/event log, UI indicators | Open |
| UDQ-REQ-EVT-001 | Alarm lifecycle shall distinguish event generation, alarm assertion, return-to-normal, latching, shelving, suppression, and acknowledgment. | UDQ-EVT-SPEC-001 | UDQ-UI-SPEC-001, UDQ-UI-SPEC-002 | alarm lifecycle test suite | alarm timeline export, screenshots | Open |
| UDQ-REQ-EVT-002 | Acknowledgment shall never erase historical alarm truth and shall remain attributable to actor, session, and time. | UDQ-EVT-SPEC-001, UDQ-HIS-SPEC-001 | UDQ-SEC-SPEC-001, UDQ-EXP-SPEC-001 | ack audit test | event log, acknowledgment record | Open |
| UDQ-REQ-DIAG-001 | Diagnostics shall synthesize layered health across platform, backend, device, protocol, signal, output, and historian domains. | UDQ-DIAG-SPEC-001 | UDQ-UI-SPEC-001, UDQ-UI-SPEC-002 | health synthesis test | diagnostics export, UI status states | Open |
| UDQ-REQ-DIAG-002 | Watchdog behavior, heartbeat loss, degradation, and recovery shall be visible and evidence-producing. | UDQ-DIAG-SPEC-001 | UDQ-EVT-SPEC-001, UDQ-HIS-SPEC-001 | fault injection test | watchdog event stream, diagnostics report | Open |
| UDQ-REQ-PROF-001 | Profiles, autosave, and restore shall preserve user/session continuity without silently implying restored live machine state. | UDQ-PROF-SPEC-001, UDQ-UI-MOD-001 | UDQ-UI-SPEC-000, UDQ-UI-SPEC-001 | save/restore test, stale restore review | restore log, screenshots | Open |
| UDQ-REQ-PROF-002 | Layout persistence and profile restore shall preserve workspace arrangements, subject to current live capability and authorization checks. | UDQ-PROF-SPEC-001 | UDQ-UI-SPEC-000, UDQ-SEC-SPEC-001 | layout restore test | profile export, interaction trace | Open |
| UDQ-REQ-DEV-001 | Device adapters shall provide a generalized abstraction layer above specific protocols while exposing capability, health, identity, and point metadata consistently. | UDQ-DEV-SPEC-001 | UDQ-DIAG-SPEC-001, UDQ-UI-SPEC-001 | adapter conformance review | capability export, diagnostics inventory | Open |
| UDQ-REQ-DEV-002 | Device-specific raw protocol detail shall remain available for service workflows without polluting ordinary operator workflows. | UDQ-DEV-SPEC-001, UDQ-UI-NAR-001 | UDQ-UI-SPEC-001, UDQ-UI-SPEC-005 | operator/service workflow review | screenshots, role-based walkthrough | Open |
| UDQ-REQ-EXP-001 | Exports and review bundles shall preserve provenance, baseline, timestamp, and covered evidence scope. | UDQ-EXP-SPEC-001, UDQ-SCM-STD-001 | UDQ-REL-SPEC-001, UDQ-PROOF-TPL-001 | export inspection | evidence bundle manifest | Open |
| UDQ-REQ-EXP-002 | Review/export surfaces shall allow operators and reviewers to distinguish raw evidence from interpreted summaries. | UDQ-EXP-SPEC-001 | UDQ-UI-SPEC-001, UDQ-UI-SPEC-004 | review workflow test | export package, summary + raw attachments | Open |
| UDQ-REQ-SEC-001 | Roles and permissions shall be backend-enforced, not merely UI-hidden. | UDQ-SEC-SPEC-001 | UDQ-REM-SPEC-001, UDQ-UI-SPEC-005 | authorization negative test | denial events, role policy export | Open |
| UDQ-REQ-SEC-002 | Command authorization decisions shall remain attributable, reviewable, and linked to session, actor, and target action. | UDQ-SEC-SPEC-001, UDQ-HIS-SPEC-001 | UDQ-EXP-SPEC-001 | command audit review | command authorization log | Open |
| UDQ-REQ-UI-001 | The shell shall preserve a graph-dominant operating posture with dockable control surfaces and recoverable workspace layout. | UDQ-UI-SPEC-000, UDQ-UI-ARCH-001 | UDQ-PROF-SPEC-001 | shell review, layout persistence test | screenshots, profile restore evidence | Open |
| UDQ-REQ-UI-002 | Workspace pages shall separate overview, devices, signals, outputs, rules, sequences, diagnostics, historian/review, and remote surfaces without ambiguity of purpose. | UDQ-UI-SPEC-001 | UDQ-UI-SPEC-000, UDQ-UI-SPEC-005 | page inventory review | UI map screenshots | Open |
| UDQ-REQ-UI-003 | Graphing shall support live, review, and live-trace modes with explicit mode indicators and return-to-live behavior. | UDQ-UI-SPEC-004 | UDQ-HIS-SPEC-001, UDQ-PROF-SPEC-001 | graph mode test | screenshots, interaction trace | Open |
| UDQ-REQ-UI-004 | The graphing surface shall support event, alarm, command, rule, and sequence overlays where evidence relationships are relevant. | UDQ-UI-SPEC-004, UDQ-HIS-SPEC-001 | UDQ-EVT-SPEC-001, UDQ-EXP-SPEC-001 | overlay rendering test | export capture, screenshots | Open |
| UDQ-REQ-UI-005 | The rules editor shall provide deterministic roundtrip behavior between visual authoring and function-style DSL authoring. | UDQ-UI-SPEC-003, UDQ-LOG-SPEC-001 | UDQ-PROOF-TPL-001 | roundtrip parity test | proof bundle | Open |
| UDQ-REQ-UI-006 | Widget language shall distinguish live, stale, invalid, disconnected, simulated, blocked, pending, acknowledged, manual, sequence, rule, and remote states in a consistent manner. | UDQ-UI-SPEC-002 | UDQ-EVT-SPEC-001, UDQ-DIAG-SPEC-001, UDQ-REM-SPEC-001 | visual language review matrix | screenshot set, style reference | Open |
| UDQ-REQ-UI-007 | Remote UI surfaces shall reflect remote capability limits and latency/connectivity truth explicitly rather than mimicking local parity when parity does not exist. | UDQ-UI-SPEC-005, UDQ-REM-SPEC-001 | UDQ-SEC-SPEC-001 | remote/local contrast review | remote screenshots, session log | Open |
| UDQ-REQ-AUD-001 | Every send-out package shall be auditable by the package-root audit tool and governed package audit specification. | UDQ-AUD-SPEC-001, UDQ-REL-SPEC-001 | UDQ-AUD-TPL-001 | audit tool run | audit report, manifest | Open |
| UDQ-REQ-AUD-002 | Draft-residue/anti-pattern scanning shall use rule-scoped allowed-pattern logic by document class and shall not permit structural-integrity waivers. | UDQ-AUD-SPEC-002, UDQ-GOV-SPEC-002 | UDQ-AUD-TPL-002 | scan rule review | scan report | Open |
| UDQ-REQ-AUD-003 | The package-root master auditor shall perform structure, semantic, contradiction, and duplication audits for hardening packages. | UDQ-AUD-SPEC-001, UDQ-GOV-REG-001, UDQ-GOV-REG-002 | UDQ-IMP-PLAN-001 | audit profile run, finding review | audit report, governed registers | Open |
| UDQ-REQ-REL-001 | Every release package shall declare package ID, code baseline ID, document baseline ID, compatibility statement, included artifacts, and change summary. | UDQ-SCM-STD-001, UDQ-REL-SPEC-001 | UDQ-REL-TPL-001, UDQ-REL-TPL-002 | package composition audit | manifest, release notes | Open |
| UDQ-REQ-QUAL-001 | Completion claims shall be supported by explicit proof bundles rather than narrative assertion alone. | UDQ-QUAL-DEF-001, UDQ-QUAL-SPEC-002 | UDQ-PROOF-TPL-001 | proof review | proof bundle | Open |
| UDQ-REQ-GOV-001 | Controlled documents, requirement IDs, and cross-references shall remain machine-readable and internally consistent across the active corpus. | UDQ-GOV-STD-001, UDQ-GOV-SPEC-002 | UDQ-AUD-SPEC-001 | registry lint, audit run | registry artifacts, audit report | Open |
| UDQ-REQ-GOV-002 | Every project-critical term shall have one canonical owner, declared alias policy, and governed anti-conflation treatment. | UDQ-GOV-GLO-001, UDQ-GOV-STD-002 | UDQ-GOV-REG-001, UDQ-GOV-REG-002 | semantic review, term-matrix inspection | term-usage matrix, audit report | Open |
| UDQ-REQ-GOV-003 | Material contradictions and semantic ambiguities shall be registered, resolved, or explicitly elevated before downstream implementation relies on them. | UDQ-GOV-STD-002, UDQ-GOV-REG-001 | UDQ-IMP-PLAN-001 | contradiction review | contradiction register, consistency report | Open |
| UDQ-REQ-GOV-004 | Meaningful duplication in normative content shall be classified as intentional, governed boilerplate, shadow definition, or consolidation-required before release-candidate use. | UDQ-GOV-STD-002, UDQ-GOV-REG-002 | UDQ-AUD-SPEC-001 | duplication review | duplication register, audit report | Open |
| UDQ-REQ-IMPL-001 | Future implementation packages shall be anchored to a governed file/module structure with declared boundary rules. | UDQ-IMP-MAP-001, UDQ-IMP-PLAN-001 | UDQ-AUD-SPEC-001 | architecture review | module-boundary map, audit report | Open |
