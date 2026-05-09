---
document_id: UDQ-HIS-SPEC-001
title: Historian, Events, and Evidence Specification
revision: r1
status: WIP
document_class: subsystem_spec
owner: UniversalDAQ
depends_on:
  - UDQ-ARCH-NAR-001
  - UDQ-ARCH-NAR-002
  - UDQ-REQ-MAT-001
  - UDQ-QUAL-DEF-001
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-MOD-001
  - UDQ-SIG-SPEC-001
  - UDQ-OUT-SPEC-001
  - UDQ-SEQ-SPEC-001
supersedes:
  - UDQ-HIS-SPEC-001__Historian_Events_and_Evidence_Specification__r0__WIP.md
---

# Historian, Events, and Evidence Specification [SEC:UDQ-HIS-SPEC-001::0]

## Revision History [SEC:UDQ-HIS-SPEC-001::0.1]
- r1: Machine-readable normalization pass, unique section anchors, metadata cleanup, and content polish against the current governed corpus.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-HIS-SPEC-001::1]

This specification defines how UniversalDAQ shall record, preserve, expose, and export runtime history, events, and evidence. It establishes the historian as a first-class platform subsystem rather than an optional afterthought.

The document also defines how event records, alarms, command traces, sequence traces, rule traces, diagnostics, exports, and package-ready evidence shall relate to one another so that the platform can support review, debugging, auditing, commissioning, and release decisions.

## 2. Scope [SEC:UDQ-HIS-SPEC-001::2]

This specification covers:
- time-series historian behavior
- event and alarm records
- command and ownership trace records
- rule and sequence evaluation trace records
- diagnostics and platform-health evidence
- review and export obligations
- evidence capture for troubleshooting, package audits, and release proof

This specification does not yet define exact database schemas or file layouts at implementation level. That belongs in later schema and storage detail documents.

## 3. Governing Principles [SEC:UDQ-HIS-SPEC-001::3]

## 3.1 Historian Is a Core Subsystem [SEC:UDQ-HIS-SPEC-001::3.1]
The historian shall be treated as a core subsystem of UniversalDAQ. It shall not be optional in the architectural sense, even if particular deployments scale its storage scope up or down.

## 3.2 Evidence Must Be Trustworthy [SEC:UDQ-HIS-SPEC-001::3.2]
Recorded history and events shall be attributable, timestamped, quality-aware, and resistant to ambiguity. The platform shall make it possible to distinguish measured fact, derived fact, requested action, applied action, observed result, inferred condition, and operator annotation.

## 3.3 Review Must Explain, Not Merely Replay [SEC:UDQ-HIS-SPEC-001::3.3]
Historical review shall support not only values over time, but also explanation of why the system behaved the way it did. This includes rule truth transitions, sequence state transitions, output ownership changes, interlocks, and safe-state triggers.

## 3.4 Live and Historical Views Must Not Be Confused [SEC:UDQ-HIS-SPEC-001::3.4]
The UI and exported artifacts shall distinguish live supervision from historical review. A user must not be able to mistake an archived trace or stale replay for current machine state.

## 3.5 Failure of One Evidence Path Must Not Silently Destroy All Evidence [SEC:UDQ-HIS-SPEC-001::3.5]
The platform shall support layered evidence generation. Failure of a convenience export path shall not imply loss of primary runtime history. Failure of a summary/log view shall not imply loss of the canonical historian record.

## 4. Core Evidence Domains [SEC:UDQ-HIS-SPEC-001::4]

UniversalDAQ shall support at least the following evidence domains.

## 4.1 Time-Series Signal History [SEC:UDQ-HIS-SPEC-001::4.1]
Historical values of raw, normalized, imported, virtual, and derived signals, recorded with timestamp and quality context.

## 4.2 Events [SEC:UDQ-HIS-SPEC-001::4.2]
Discrete timestamped records describing noteworthy transitions or occurrences.

Examples include:
- device connection established/lost
- sequence started/paused/resumed/completed/aborted
- output owner changed
- rule entered true/false/blocked/indeterminate state
- profile applied
- backend entered degraded mode
- historian rollover occurred

## 4.3 Alarms and Faults [SEC:UDQ-HIS-SPEC-001::4.3]
Alarm/fault assertions, clears, acknowledgments, latches, shelving if implemented later, and related operator actions.

## 4.4 Commands and Output Trace [SEC:UDQ-HIS-SPEC-001::4.4]
Requests, arbitration outcomes, applied outputs, observed results where observable, and blocks/inhibits.

## 4.5 Rules and Logic Trace [SEC:UDQ-HIS-SPEC-001::4.5]
Rule evaluation state changes, condition-group transitions, blocked reasons, quality-caused indeterminacy, and action-request outcomes.

## 4.6 Sequence and Workflow Trace [SEC:UDQ-HIS-SPEC-001::4.6]
Runtime sequence state changes, step entry/exit, parameter bindings, holds, waits, timeouts, aborts, restarts, and recovery transitions.

## 4.7 Diagnostics and Platform Health [SEC:UDQ-HIS-SPEC-001::4.7]
Evidence of communication health, queue pressure, poll failures, reconnects, write failures, watchdog action, backend health, historian health, and export health.

## 4.8 Human Annotations and Release Evidence [SEC:UDQ-HIS-SPEC-001::4.8]
Optional operator/engineer notes, run annotations, review conclusions, test identifiers, package audit artifacts, and release evidence bundles.

## 5. Canonical Historian Concepts [SEC:UDQ-HIS-SPEC-001::5]

## 5.1 History Record Types [SEC:UDQ-HIS-SPEC-001::5.1]
The platform shall distinguish between at least these conceptual record types:
- sampled time-series record
- event record
- alarm/fault record
- command/request record
- arbitration decision record
- output-application record
- sequence record
- rule-trace record
- diagnostic record
- annotation record
- export/package evidence record

A given storage implementation may optimize these physically, but the logical distinctions shall remain explicit.

## 5.2 Canonical Time Reference [SEC:UDQ-HIS-SPEC-001::5.2]
All persisted records shall carry a canonical event time. Where relevant, records may additionally carry:
- source/device timestamp
- backend receipt time
- persistence/write time

If multiple timestamps exist, their semantics shall be explicit.

## 5.3 Identity and Correlation [SEC:UDQ-HIS-SPEC-001::5.3]
The platform shall support correlation between related records, such as:
- command request ↔ arbitration decision ↔ applied write ↔ observed result
- sequence runtime instance ↔ step events ↔ output requests ↔ faults
- rule revision ↔ rule truth transitions ↔ output requests
- alarm assertion ↔ acknowledgment ↔ clear

Review tools shall be able to navigate these relationships.

## 6. Time-Series Historian Specification [SEC:UDQ-HIS-SPEC-001::6]

## 6.1 Historized Signal Eligibility [SEC:UDQ-HIS-SPEC-001::6.1]
Not every internal value must be historized at the same rate, but the platform shall define a clear policy for whether a signal is:
- always historized
- historized when enabled/configured
- historized only on change
- historized only in diagnostic mode
- not historized

This policy shall be explicit, not accidental.

## 6.2 Recorded Fields for Time-Series Signals [SEC:UDQ-HIS-SPEC-001::6.2]
A historized time-series record shall be able to carry at least:
- signal identity
- timestamp
- value
- quality state
- units context or units identity
- source/type context as needed

Where useful, a record may also carry:
- sequence/runtime context
- batch/session/run identifier
- revision/config identifier
- source timestamp

## 6.3 Sampling and On-Change Policies [SEC:UDQ-HIS-SPEC-001::6.3]
The historian shall support a mixture of:
- fixed-rate sampling
- on-change logging
- event-driven snapshot capture
- aggregated/decimated review retrieval for performance

Review decimation shall not silently redefine the canonical stored record. Retrieval simplification for UI performance shall be distinct from primary storage truth.

## 6.4 Quality Preservation [SEC:UDQ-HIS-SPEC-001::6.4]
Signal quality shall be preserved with historical records. The platform shall not silently strip quality context and leave a value appearing cleaner than it was in runtime.

## 6.5 Derived Signal History [SEC:UDQ-HIS-SPEC-001::6.5]
Derived signals may be historized either as explicitly stored records or reproducible computed views depending on future implementation decisions, but the platform must make the chosen behavior explicit. If derived histories are persisted, their provenance must remain traceable.

## 7. Event Model Specification [SEC:UDQ-HIS-SPEC-001::7]

## 7.1 Event Meaning [SEC:UDQ-HIS-SPEC-001::7.1]
An event is a discrete notable occurrence or transition. Events shall be used for explainability, auditability, and operational review.

## 7.2 Minimum Event Fields [SEC:UDQ-HIS-SPEC-001::7.2]
An event record shall support at least:
- event timestamp
- event type/category
- origin subsystem
- severity or importance level where relevant
- concise message/summary
- machine-readable structured context
- correlation identifiers where relevant

## 7.3 Event Categories [SEC:UDQ-HIS-SPEC-001::7.3]
The platform shall support event categorization at least across:
- connectivity/comms
- signal quality/state
- alarm/fault
- rule/logic
- command/output
- sequence/workflow
- historian/storage/export
- profile/configuration/session
- diagnostics/platform health
- user/remote action

## 7.4 Event Severity Doctrine [SEC:UDQ-HIS-SPEC-001::7.4]
Not all events are alarms. The platform shall distinguish informational events, warnings, operationally important transitions, and faults requiring intervention.

## 8. Alarm and Fault Records [SEC:UDQ-HIS-SPEC-001::8]

## 8.1 Alarm/Failure Lifecycle [SEC:UDQ-HIS-SPEC-001::8.1]
Alarm and fault records shall support explicit lifecycle transitions such as:
- asserted
- acknowledged
- cleared
- latched cleared pending reset if applicable
- suppressed/shelved if implemented later

## 8.2 Alarm Evidence Requirements [SEC:UDQ-HIS-SPEC-001::8.2]
Alarm review shall show at least:
- what asserted
- when it asserted
- whether it was acknowledged
- who/what acknowledged it if attributable
- when it cleared
- whether it contributed to hold/abort/safe-state behavior

## 8.3 Alarm vs Event Separation [SEC:UDQ-HIS-SPEC-001::8.3]
Alarm/fault records may be implemented alongside the event system, but review tools must still allow operators and engineers to distinguish alarm lifecycle from general informational events.

## 9. Command, Arbitration, and Output Evidence [SEC:UDQ-HIS-SPEC-001::9]

## 9.1 Command Request Recording [SEC:UDQ-HIS-SPEC-001::9.1]
Every meaningful command request shall be recordable with:
- requested target
- requested state/value
- request origin
- request time
- requester identity/context if available
- mode/context

## 9.2 Arbitration Decision Recording [SEC:UDQ-HIS-SPEC-001::9.2]
If a request is blocked, superseded, denied, overridden, or accepted, that outcome shall be recordable. The system must not leave later reviewers guessing why a requested action did not take effect.

## 9.3 Applied vs Requested Distinction [SEC:UDQ-HIS-SPEC-001::9.3]
The historian/evidence model shall support distinction between:
- requested command
- approved command
- applied write/action
- observed resulting state

These concepts are related but not identical.

## 9.4 Safe-State Traceability [SEC:UDQ-HIS-SPEC-001::9.4]
Entry into safe-state, maintenance of safe-state, and exit from safe-state shall all be visible in event/evidence history.

## 10. Rule and Logic Evidence [SEC:UDQ-HIS-SPEC-001::10]

## 10.1 Rule Trace Purpose [SEC:UDQ-HIS-SPEC-001::10.1]
Rule evidence shall make it possible to answer:
- why a rule became true or false
- why a rule became blocked or indeterminate
- which dependency changed last
- whether quality/staleness caused inhibition
- what action requests resulted

## 10.2 Minimum Rule Trace Information [SEC:UDQ-HIS-SPEC-001::10.2]
Rule trace capability shall support:
- rule identity and revision
- state transition time
- prior state and new state
- blocking reason if any
- changed dependency context where available
- resulting action request or no-action result

## 10.3 Explainability Over Raw Verbosity [SEC:UDQ-HIS-SPEC-001::10.3]
The platform should favor meaningful transition/event trace over excessively verbose per-scan flooding. However, deeper diagnostic trace modes may exist for engineering use.

## 11. Sequence and Workflow Evidence [SEC:UDQ-HIS-SPEC-001::11]

## 11.1 Sequence Runtime Identity [SEC:UDQ-HIS-SPEC-001::11.1]
Sequence evidence shall distinguish between sequence definitions and runtime instances.

## 11.2 Minimum Sequence Trace Information [SEC:UDQ-HIS-SPEC-001::11.2]
A sequence/workflow runtime shall support evidence for:
- start time
- initiating origin/context
- parameter set or parameter revision context
- step entry/exit
- waits/holds/pauses
- timeout/fault transitions
- completion/abort/reset

## 11.3 Linkage to Outputs and Rules [SEC:UDQ-HIS-SPEC-001::11.3]
Where a sequence request results in output requests or is gated by rules/interlocks, evidence should support correlation so a reviewer can reconstruct causality.

## 12. Diagnostics and Platform Health Evidence [SEC:UDQ-HIS-SPEC-001::12]

## 12.1 Diagnostics Are First-Class Evidence [SEC:UDQ-HIS-SPEC-001::12.1]
Diagnostics shall not exist only as transient console output. Meaningful platform health transitions shall be recordable and reviewable.

## 12.2 Diagnostic Categories [SEC:UDQ-HIS-SPEC-001::12.2]
Diagnostic evidence shall be able to include at least:
- device connect/disconnect/reconnect
- poll failures/timeouts
- write failures/retries
- queue backlog or publish lag
- historian write issues
- storage rollover conditions
- export failures
- backend degraded state transitions
- watchdog actions

## 12.3 Health vs Noise [SEC:UDQ-HIS-SPEC-001::12.3]
The platform shall distinguish persistent operational health signals from noisy low-level chatter. It should support rate-limiting or aggregation where appropriate without hiding important state changes.

## 13. Sessions, Runs, and Review Context [SEC:UDQ-HIS-SPEC-001::13]

## 13.1 Session/Run Context [SEC:UDQ-HIS-SPEC-001::13.1]
The platform should support the concept of a session, run, or experiment/review context so that stored evidence can be grouped meaningfully.

Examples may include:
- application launch session
- acquisition session
- sequence run instance
- commissioning test run
- overnight logging run
- release verification run

## 13.2 Context Annotation [SEC:UDQ-HIS-SPEC-001::13.2]
The system should allow at least structured context identifiers and later may support freeform notes/annotations associated with sessions or runs.

## 13.3 Revision Context [SEC:UDQ-HIS-SPEC-001::13.3]
Where practical, stored evidence should be attributable to configuration/runtime revision context so that later reviewers know which logic, signal definitions, and platform behavior were active.

## 14. Review and Visualization Obligations [SEC:UDQ-HIS-SPEC-001::14]

## 14.1 Live vs Historical Review [SEC:UDQ-HIS-SPEC-001::14.1]
The UI shall distinguish:
- live supervision
- historical review
- session replay/explore modes
- return-to-live behavior

## 14.2 Graph Review Modes [SEC:UDQ-HIS-SPEC-001::14.2]
The platform shall support graph/trend review patterns aligned with preserved Genesys strengths, including concepts such as:
- sliding-window live view
- whole-session review
- explore/pan historical navigation
- explicit return-to-live

## 14.3 Event/Trace Review [SEC:UDQ-HIS-SPEC-001::14.3]
Users shall be able to review events/alarms/diagnostics in a way that supports filtering by:
- time range
- subsystem
- severity/category
- device
- rule
- sequence instance
- target/output

## 14.4 Explainability Integration [SEC:UDQ-HIS-SPEC-001::14.4]
Historical review should allow cross-navigation between:
- traces
- events
- alarms
- rules
- sequences
- outputs
- diagnostics

Review shall help answer “what happened and why,” not merely show disconnected lists.

## 15. Export and Evidence Package Obligations [SEC:UDQ-HIS-SPEC-001::15]

## 15.1 Export Is Required but Secondary to Canonical Storage [SEC:UDQ-HIS-SPEC-001::15.1]
Exports such as CSV, snapshot reports, or evidence bundles are required capabilities, but they are derivative views of the canonical evidence model.

## 15.2 Minimum Export Concepts [SEC:UDQ-HIS-SPEC-001::15.2]
The platform shall eventually support export concepts such as:
- signal history export
- selected time-window export
- alarm/event export
- diagnostic export
- sequence run evidence export
- package audit evidence export

## 15.3 Provenance of Exports [SEC:UDQ-HIS-SPEC-001::15.3]
Exports shall preserve enough provenance to show:
- source platform/session context
- export time
- selected range or filter context
- relevant revision/config context where practical

## 15.4 Evidence Bundles [SEC:UDQ-HIS-SPEC-001::15.4]
The platform should support future packaging of multi-artifact evidence bundles for verification and release work. These may include logs, trend exports, configuration snapshots, diagnostics summaries, and audit check outputs.

## 16. Persistence, Retention, and Rollover Doctrine [SEC:UDQ-HIS-SPEC-001::16]

## 16.1 Retention Policy Must Be Explicit [SEC:UDQ-HIS-SPEC-001::16.1]
Historian retention, rollover, archival, and pruning behavior shall be explicit and configurable at policy level.

## 16.2 Rollover Must Be Traceable [SEC:UDQ-HIS-SPEC-001::16.2]
When rollover, partitioning, or archival occurs, the system shall emit evidence/events so later review is not confused by apparent discontinuities.

## 16.3 Data Loss Must Be Visible [SEC:UDQ-HIS-SPEC-001::16.3]
If records are dropped, storage fails, or evidence continuity is compromised, the system shall generate visible diagnostic evidence rather than silently presenting an incomplete history as complete.

## 17. Remote Observation and Multi-Client Implications [SEC:UDQ-HIS-SPEC-001::17]

## 17.1 Shared Evidence Truth [SEC:UDQ-HIS-SPEC-001::17.1]
Remote and local clients shall observe the same backend-authoritative evidence truth, subject only to legitimate filtering/permission differences.

## 17.2 Remote Actions Must Be Attributable [SEC:UDQ-HIS-SPEC-001::17.2]
Remote acknowledgments, command requests, and supervisory actions must be attributable in the evidence model.

## 17.3 Multi-Client Review Consistency [SEC:UDQ-HIS-SPEC-001::17.3]
Historical review semantics shall be consistent across local and remote clients. A client-specific view may differ in convenience presentation, but not in the meaning of the stored evidence.

## 18. Validation and Integrity Requirements [SEC:UDQ-HIS-SPEC-001::18]

## 18.1 Record Integrity [SEC:UDQ-HIS-SPEC-001::18.1]
The system shall preserve enough structure to avoid ambiguous reconstruction of key transitions.

## 18.2 Ordering and Causality [SEC:UDQ-HIS-SPEC-001::18.2]
Where events are very close in time, the platform should preserve ordering/correlation information sufficient for debugging and audit work.

## 18.3 Schema Validation [SEC:UDQ-HIS-SPEC-001::18.3]
Future implementation shall validate evidence records and export artifacts against defined schemas/configured expectations.

## 18.4 Regression Sensitivity [SEC:UDQ-HIS-SPEC-001::18.4]
Changes to historian/event/evidence behavior shall be treated as high-risk changes because they directly affect trust, debugging, and release proof.

## 19. UI Obligations [SEC:UDQ-HIS-SPEC-001::19]

The UI shall:
- present live and historical modes distinctly
- expose event/alarm/diagnostic review as first-class workspaces or panes
- show output/rule/sequence causality where possible
- make review navigation practical for long runs
- support export initiation and export result visibility
- expose historian health and evidence continuity status

The UI shall not:
- imply completeness when history is partial or degraded
- blur live and historical views
- hide blocked commands or missing evidence continuity

## 20. Implementation Phasing Guidance [SEC:UDQ-HIS-SPEC-001::20]

## 20.1 First Serious Implementation Target [SEC:UDQ-HIS-SPEC-001::20.1]
Early implementation should provide at least:
- robust time-series historian for selected signals
- event log with meaningful categories
- alarm/fault lifecycle records
- command/arbitration trace basics
- sequence trace basics
- graph review with live/history separation
- CSV and core export capability
- historian health diagnostics

## 20.2 Later Expansion Targets [SEC:UDQ-HIS-SPEC-001::20.2]
Later phases may expand into:
- richer evidence bundles
- annotations and run notes
- replay-oriented tools
- deeper rule trace and dependency explainers
- retention/archival tooling
- more advanced search and cross-correlation features

## 21. Anti-Patterns [SEC:UDQ-HIS-SPEC-001::21]

The following are explicitly disallowed:
- treating historian/export as optional polish
- silently losing evidence continuity
- conflating requested, applied, and observed output state
- exposing historical values without quality context when that context matters
- allowing live and historical review modes to become visually ambiguous
- using decimated UI retrieval as if it were the canonical stored truth
- storing events with no attributable origin or meaning
- reducing diagnostics to transient console spam only

## 22. Downstream Consequences [SEC:UDQ-HIS-SPEC-001::22]

This specification shall drive later work in:
- historian storage/schema specification
- event/alarm schema specification
- export/evidence bundle specification
- UI review workspace/page specifications
- audit/proof model documents
- completeness and traceability updates where needed
