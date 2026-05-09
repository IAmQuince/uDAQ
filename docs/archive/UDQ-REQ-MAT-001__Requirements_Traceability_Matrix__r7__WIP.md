---
document_id: "UDQ-REQ-MAT-001"
title: "Requirements Traceability Matrix"
revision: "r7"
status: "WIP"
document_class: "requirement_matrix"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-SPEC-003"
  - "UDQ-GOV-SPEC-004"
  - "UDQ-GOV-SPEC-005"
  - "UDQ-GOV-SPEC-006"
supersedes:
  - "UDQ-REQ-MAT-001__Requirements_Traceability_Matrix__r6__WIP.md"
revision_history:
  - "r7 | 2026-03-21 | Added governance-control-tower readiness states and linked requirements to execution-contract, invariant, worked-example, and decision posture."
  - "r6 | 2026-03-21 | Implementation-entry statuses introduced."
---
# Requirements Traceability Matrix [SEC:UDQ-REQ-MAT-001::0]

    ## 1. Purpose [SEC:UDQ-REQ-MAT-001::1]

    This matrix now expresses governance-aware implementation-entry posture rather than only semantic readiness.

    ## 2. Status vocabulary [SEC:UDQ-REQ-MAT-001::2]

    - `SEMANTICALLY_CLOSED` — Meaning is governed and contradictions are closed, but the requirement has not yet been attached to the first implementation contract.
- `CONTRACT_DEFINED` — The requirement is represented in the execution contract or equivalent package-governance infrastructure, but runtime invariants are not yet the main driver.
- `INVARIANT_DEFINED` — The requirement is in the first allowed implementation slice and now has explicit invariant posture.
- `BLOCKED_BY_DECISION` — The requirement remains governed but is intentionally blocked by an active decision-log item.
- `DEFERRED` — The requirement is intentionally pushed beyond the first implementation-entry slice.


    ## 3. Current matrix [SEC:UDQ-REQ-MAT-001::3]

    | Requirement ID | Statement | Status | Contract | Invariants | Worked Examples | Decision | First Slice / Module Area |
|---|---|---|---|---|---|---|---|
| UDQ-REQ-ARCH-001 | The backend shall remain the authoritative source of runtime truth, c... | INVARIANT_DEFINED | DEFINED | DEFINED | COVERED | CLOSED | baseline-shell-signal-historian / src/universaldaq/app + src/universaldaq/common |
| UDQ-REQ-ARCH-002 | The UI shall never silently imply authority that it does not possess. | INVARIANT_DEFINED | DEFINED | DEFINED | COVERED | CLOSED | baseline-shell-signal-historian / src/universaldaq/app + src/universaldaq/common |
| UDQ-REQ-SIG-001 | Every signal shall have stable identity independent of user-facing di... | INVARIANT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | baseline-shell-signal-historian / src/universaldaq/signals |
| UDQ-REQ-SIG-002 | Derived signals shall be dependency-tracked and cycle-checked before ... | INVARIANT_DEFINED | DEFINED | DEFINED | PLANNED | CLOSED | baseline-shell-signal-historian / src/universaldaq/signals |
| UDQ-REQ-OUT-001 | Output actions shall be requests subject to arbitration, permissives,... | BLOCKED_BY_DECISION | PLANNED | DEFINED | COVERED | OPEN | deferred-control-surface / src/universaldaq/outputs |
| UDQ-REQ-OUT-002 | Requested, applied, and observed output states shall be distinguishab... | BLOCKED_BY_DECISION | PLANNED | DEFINED | COVERED | OPEN | deferred-control-surface / src/universaldaq/outputs |
| UDQ-REQ-RULE-001 | Rules shall be represented by one canonical model with equivalent vis... | DEFERRED | PLANNED | PLANNED | PLANNED | DEFERRED | later-slice / src/universaldaq/rules |
| UDQ-REQ-RULE-002 | Rule evaluation shall be explainable, including quality-blocked and i... | DEFERRED | PLANNED | PLANNED | PLANNED | DEFERRED | later-slice / src/universaldaq/rules |
| UDQ-REQ-MOD-001 | Modbus integration shall support TCP and RTU client modes with explic... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / src/universaldaq/adapters |
| UDQ-REQ-MOD-002 | Modbus-backed writable points shall participate in the same arbitrati... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | deferred-control-surface / src/universaldaq/adapters |
| UDQ-REQ-SEQ-001 | Sequences shall distinguish definition, revision, runtime instance, a... | DEFERRED | PLANNED | PLANNED | PLANNED | DEFERRED | deferred-control-surface / src/universaldaq/sequences |
| UDQ-REQ-SEQ-002 | Sequence pause, hold, resume, timeout, abort, and recovery behavior s... | DEFERRED | PLANNED | PLANNED | PLANNED | DEFERRED | deferred-control-surface / src/universaldaq/sequences |
| UDQ-REQ-HIS-001 | Historian data and event evidence shall preserve context linking runt... | INVARIANT_DEFINED | DEFINED | DEFINED | COVERED | CLOSED | baseline-shell-signal-historian / src/universaldaq/historian |
| UDQ-REQ-HIS-002 | Live and historical review modes shall remain distinct and reversible... | INVARIANT_DEFINED | DEFINED | DEFINED | COVERED | CLOSED | baseline-shell-signal-historian / src/universaldaq/historian |
| UDQ-REQ-REM-001 | Remote surfaces shall distinguish observation, supervision, and direc... | BLOCKED_BY_DECISION | PLANNED | PLANNED | PLANNED | OPEN | deferred-control-surface / src/universaldaq/remote |
| UDQ-REQ-REM-002 | Remote-issued commands shall be attributable and visible as remote-or... | BLOCKED_BY_DECISION | PLANNED | PLANNED | PLANNED | OPEN | deferred-control-surface / src/universaldaq/remote |
| UDQ-REQ-EVT-001 | Alarm lifecycle shall distinguish event generation, alarm assertion, ... | SEMANTICALLY_CLOSED | PLANNED | DEFINED | COVERED | CLOSED | deferred-control-surface / src/universaldaq/events |
| UDQ-REQ-EVT-002 | Acknowledgment shall never erase historical alarm truth and shall rem... | SEMANTICALLY_CLOSED | PLANNED | DEFINED | COVERED | CLOSED | deferred-control-surface / src/universaldaq/events |
| UDQ-REQ-DIAG-001 | Diagnostics shall synthesize layered health across platform, backend,... | SEMANTICALLY_CLOSED | PLANNED | DEFINED | PLANNED | CLOSED | later-slice / src/universaldaq/diagnostics |
| UDQ-REQ-DIAG-002 | Watchdog behavior, heartbeat loss, degradation, and recovery shall be... | SEMANTICALLY_CLOSED | PLANNED | DEFINED | PLANNED | CLOSED | later-slice / src/universaldaq/diagnostics |
| UDQ-REQ-PROF-001 | Profiles, autosave, and restore shall preserve user/session continuit... | INVARIANT_DEFINED | DEFINED | DEFINED | COVERED | CLOSED | baseline-shell-signal-historian / src/universaldaq/profiles |
| UDQ-REQ-PROF-002 | Layout persistence and profile restore shall preserve workspace arran... | INVARIANT_DEFINED | DEFINED | DEFINED | COVERED | CLOSED | baseline-shell-signal-historian / src/universaldaq/profiles |
| UDQ-REQ-DEV-001 | Device adapters shall provide a generalized abstraction layer above s... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / src/universaldaq/adapters |
| UDQ-REQ-DEV-002 | Device-specific raw protocol detail shall remain available for servic... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / src/universaldaq/adapters |
| UDQ-REQ-EXP-001 | Exports and review bundles shall preserve provenance, baseline, times... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / src/universaldaq/exports |
| UDQ-REQ-EXP-002 | Review/export surfaces shall allow operators and reviewers to disting... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / src/universaldaq/exports |
| UDQ-REQ-SEC-001 | Roles and permissions shall be backend-enforced, not merely UI-hidden. | BLOCKED_BY_DECISION | PLANNED | DEFINED | COVERED | OPEN | deferred-control-surface / src/universaldaq/security |
| UDQ-REQ-SEC-002 | Command authorization decisions shall remain attributable, reviewable... | BLOCKED_BY_DECISION | PLANNED | PLANNED | PLANNED | OPEN | deferred-control-surface / src/universaldaq/security |
| UDQ-REQ-UI-001 | The shell shall preserve a graph-dominant operating posture with dock... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / src/universaldaq/ui |
| UDQ-REQ-UI-002 | Workspace pages shall separate overview, devices, signals, outputs, r... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / src/universaldaq/ui |
| UDQ-REQ-UI-003 | Graphing shall support live, review, and live-trace modes with explic... | INVARIANT_DEFINED | DEFINED | DEFINED | COVERED | CLOSED | baseline-shell-signal-historian / src/universaldaq/ui |
| UDQ-REQ-UI-004 | The graphing surface shall support event, alarm, command, rule, and s... | INVARIANT_DEFINED | DEFINED | DEFINED | COVERED | CLOSED | baseline-shell-signal-historian / src/universaldaq/ui |
| UDQ-REQ-UI-005 | The rules editor shall provide deterministic roundtrip behavior betwe... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / src/universaldaq/ui |
| UDQ-REQ-UI-006 | Widget language shall distinguish live, stale, invalid, disconnected,... | INVARIANT_DEFINED | DEFINED | DEFINED | COVERED | CLOSED | baseline-shell-signal-historian / src/universaldaq/ui |
| UDQ-REQ-UI-007 | Remote UI surfaces shall reflect remote capability limits and latency... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / src/universaldaq/ui |
| UDQ-REQ-AUD-001 | Every send-out package shall be auditable by the package-root audit t... | CONTRACT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | package-governance / tools/traceability + registries/active + audit_reports/active |
| UDQ-REQ-AUD-002 | Draft-residue/anti-pattern scanning shall use rule-scoped allowed-pat... | CONTRACT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | package-governance / tools/traceability + registries/active + audit_reports/active |
| UDQ-REQ-AUD-003 | The package-root master auditor shall perform structure, semantic, co... | CONTRACT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | package-governance / tools/traceability + registries/active + audit_reports/active |
| UDQ-REQ-REL-001 | Every release package shall declare package ID, code baseline ID, doc... | CONTRACT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | package-governance / tools/traceability + registries/active + audit_reports/active |
| UDQ-REQ-QUAL-001 | Completion claims shall be supported by explicit proof bundles rather... | SEMANTICALLY_CLOSED | PLANNED | PLANNED | PLANNED | CLOSED | later-slice / proof/bundles |
| UDQ-REQ-GOV-001 | Controlled documents, requirement IDs, and cross-references shall rem... | CONTRACT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | package-governance / tools/traceability + registries/active + audit_reports/active |
| UDQ-REQ-GOV-002 | Every project-critical term shall have one canonical owner, declared ... | CONTRACT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | package-governance / tools/traceability + registries/active + audit_reports/active |
| UDQ-REQ-GOV-003 | Material contradictions and semantic ambiguities shall be registered,... | CONTRACT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | package-governance / tools/traceability + registries/active + audit_reports/active |
| UDQ-REQ-GOV-004 | Meaningful duplication in normative content shall be classified as in... | CONTRACT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | package-governance / tools/traceability + registries/active + audit_reports/active |
| UDQ-REQ-IMPL-001 | Future implementation packages shall be anchored to a governed file/m... | CONTRACT_DEFINED | DEFINED | PLANNED | PLANNED | CLOSED | package-governance / tools/traceability + registries/active + audit_reports/active |
