---
document_id: UDQ-DIAG-SPEC-001
title: Diagnostics, Watchdog, and Health Model Specification
revision: r0
status: WIP
classification:
  domain: DIAG
  type: SPEC
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-GOV-STD-001
- UDQ-HIS-SPEC-001
- UDQ-PROT-SPEC-001
- UDQ-REM-SPEC-001
- UDQ-UI-MOD-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
audit_exceptions: []
---
# Diagnostics, Watchdog, and Health Model Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-21 | WIP | Initial issue defining runtime diagnostics, watchdog behavior, health synthesis, and explainability obligations across the platform. |

# 1. Purpose [SEC:UDQ-DIAG-SPEC-001::1]

This specification defines how UniversalDAQ shall observe, synthesize, present, and record platform health, diagnostics, and watchdog state.

# 2. Scope [SEC:UDQ-DIAG-SPEC-001::2]

This specification applies to:

- backend runtime health
- frontend/session health where observable
- device/protocol health
- polling/execution loop health
- historian/export health
- sequence/rule evaluation health
- watchdog inputs, outputs, and actions
- diagnostic surfaces, events, and evidence

# 3. Canonical health model [SEC:UDQ-DIAG-SPEC-001::3]

UniversalDAQ shall use a layered health model rather than a single generic good/bad flag. Health shall be representable at minimum for:

- platform
- service/subsystem
- device
- protocol connection
- signal quality source
- output path
- rule engine
- sequence runtime
- historian/export pipeline
- remote publication pathway

# 4. Health states [SEC:UDQ-DIAG-SPEC-001::4]

## 4.1 Required states [SEC:UDQ-DIAG-SPEC-001::4.1]

The health model shall distinguish at minimum:

- healthy
- degraded
- faulted
- offline/disconnected
- initializing
- unknown/unverified
- maintenance/disabled where relevant

## 4.2 Truthfulness [SEC:UDQ-DIAG-SPEC-001::4.2]

Health states shall represent actual confidence and availability, not optimistic assumptions. Missing updates, stalled loops, parser failures, and publication failures shall not be reported as healthy.

# 5. Diagnostic domains [SEC:UDQ-DIAG-SPEC-001::5]

## 5.1 Runtime/process diagnostics [SEC:UDQ-DIAG-SPEC-001::5.1]

The platform shall observe core runtime processes such as:

- service startup/ready/failure state
- loop timing and overrun behavior
- queue backlog or publication lag where applicable
- unhandled exception capture pathways
- thread/task liveliness where relevant

## 5.2 Device/protocol diagnostics [SEC:UDQ-DIAG-SPEC-001::5.2]

Device and protocol diagnostics shall cover, at minimum:

- connectivity state
- transaction success/failure counts
- timeout/retry behavior
- protocol decode/encode anomalies
- heartbeat freshness where supported
- last-good communication time

## 5.3 Data path diagnostics [SEC:UDQ-DIAG-SPEC-001::5.3]

The platform shall surface diagnostics for:

- signal update staleness
- derived-signal evaluation anomalies
- rule evaluation blocks or indeterminate states
- command arbitration blocks
- historian write failures or lag
- export generation failures

# 6. Watchdog model [SEC:UDQ-DIAG-SPEC-001::6]

## 6.1 Watchdog purpose [SEC:UDQ-DIAG-SPEC-001::6.1]

Watchdogs exist to detect loss of expected liveness or progression and to support governed response.

## 6.2 Watchdog sources [SEC:UDQ-DIAG-SPEC-001::6.2]

Watchdogs may monitor, at minimum:

- backend main loop or scheduler cadence
- device polling progression
- sequence progression when progression is expected
- output-application round-trip expectations where observable
- remote publication freshness
- external heartbeat inputs

## 6.3 Watchdog actions [SEC:UDQ-DIAG-SPEC-001::6.3]

Watchdog expiration may produce, under governed policy:

- diagnostic events/alarms
- health degradation or fault transitions
- safe-state requests
- reconnection or restart attempts where allowed
- operator-visible explainability records

Watchdog actions shall remain consistent with the output and authorization model; they shall not create undocumented bypass paths.

# 7. Health synthesis [SEC:UDQ-DIAG-SPEC-001::7]

## 7.1 Upward synthesis [SEC:UDQ-DIAG-SPEC-001::7.1]

Higher-level health shall be derivable from lower-level health contributors, but the platform shall avoid losing detail when summarizing. Operators shall be able to drill down from platform-level degraded/faulted state to the contributing subsystem(s).

## 7.2 Dependency awareness [SEC:UDQ-DIAG-SPEC-001::7.2]

Health synthesis shall account for dependencies. For example, a device marked unhealthy because its underlying transport is offline should preserve both the local view and the upstream cause.

# 8. UI obligations [SEC:UDQ-DIAG-SPEC-001::8]

The UI shall provide a diagnostics/service surface capable of showing:

- current health state by domain
- heartbeat/watchdog freshness
- recent failures, retries, and recoveries
- last-good update time
- contributing causes for degraded/faulted state
- maintenance/disabled state when applicable
- links from alarms or blocked commands back to diagnostic context

# 9. Historian and evidence obligations [SEC:UDQ-DIAG-SPEC-001::9]

The historian/evidence layer shall preserve material diagnostic transitions and watchdog actions, including:

- health state transitions
- watchdog armed/expired/recovered transitions
- restart/reconnect attempts and results
- diagnostic exceptions or decode failures where policy says they are evidence-worthy
- actor identity for manual service actions when applicable

# 10. Interaction with alarms, outputs, and sequences [SEC:UDQ-DIAG-SPEC-001::10]

Diagnostics shall integrate with other subsystems without ambiguity.

- health degradation may raise alarms or inhibit commands
- watchdog expiry may hold or abort sequences under governed policy
- communication failure may force signal quality transitions and output safe-state actions
- restoration of health shall not silently erase prior evidence or imply completed operator review

# 11. Recovery doctrine [SEC:UDQ-DIAG-SPEC-001::11]

Recovery behavior shall be explicit. The platform shall distinguish between:

- automatic recovery attempts
- recovery success
- recovery failure
- operator-directed service intervention
- restart/reconnect with continuity restoration

The UI shall make it clear whether a system is merely back online or fully restored to prior continuity expectations.

# 12. Remote and multi-client implications [SEC:UDQ-DIAG-SPEC-001::12]

Remote observers and supervisors shall be able to see health and diagnostic state appropriate to their authorization level. Health truth shall remain backend-authoritative so that multiple clients do not infer different system condition from the same runtime facts.

# 13. Validation and test obligations [SEC:UDQ-DIAG-SPEC-001::13]

The diagnostics/watchdog subsystem shall be testable for:

- loop stall detection
- communication timeout and recovery
- historian failure visibility
- rule/sequence anomaly surfacing
- health synthesis correctness
- safe-state trigger interactions
- restart/reconnect evidence continuity

# 14. Anti-patterns [SEC:UDQ-DIAG-SPEC-001::14]

The platform shall avoid:

- green/healthy status that masks stale or missing updates
- watchdog logic that acts without evidence or explainability
- health summaries that hide the underlying fault path
- retries/recovery loops that remain invisible to operators
- diagnostic state that exists only in logs and not in governed UI/evidence surfaces


# 7. Runtime evidence layering [SEC:UDQ-DIAG-SPEC-001::7]
The bounded implementation now separates reviewer-facing runtime rollups from engineering diagnostics and raw instrumentation. Diagnostic snapshots remain evidence surfaces and shall not be promoted into incidents without an explicit event category.

# 9A. Session flight record for the first bench slice [SEC:UDQ-DIAG-SPEC-001::9A]

The bounded operator-flow slice shall provide a text-first session flight record that can be generated without a GUI-specific dependency chain. For the first bench slice, that flight record shall combine:
- trusted-session inventory
- first-signal replay tape / bounded trace preview
- control posture and actor/session identity
- recent shell action audit entries
- recent runtime/session events
- active alarm summary and recent domain events

This flight record is intentionally narrower than the eventual full historian/replay system, but it establishes the canonical seam for reproducible debugging, copy-paste support diagnostics, and future richer replay tooling.


## Bench continuity diagnostic extension

The diagnostics layer shall surface what persistence state was saved, what state was restored, what state was intentionally left historical-only, and what persisted preference or session-summary element was skipped during restore. Operator notes shall be countable and attributable in the persistence diagnostic output without being conflated with system-generated events.
