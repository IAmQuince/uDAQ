---
document_id: UDQ-REM-SPEC-001
title: Remote Observation and Supervision Specification
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
  - "UDQ-SIG-SPEC-001"
  - "UDQ-OUT-SPEC-001"
  - "UDQ-HIS-SPEC-001"
  - "UDQ-LOG-SPEC-001"
  - "UDQ-PROT-SPEC-001"
  - "UDQ-SEQ-SPEC-001"
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-STD-002"
  - "UDQ-SEC-SPEC-001"
supersedes:
  - "UDQ-REM-SPEC-001__Remote_Observation_and_Supervision_Specification__r1__WIP.md"
revision_history:
  - "r2 | 2026-03-21 | Subsystem reconciliation pass: clarified remote capability boundaries, origin attribution, and non-parity doctrine."
  - "r1 | 2026-03-21 | Prior active revision carried forward before subsystem reconciliation pass."
---
# Remote Observation and Supervision Specification [SEC:UDQ-REM-SPEC-001::0]

## Revision History [SEC:UDQ-REM-SPEC-001::0.1]
- r2: Subsystem reconciliation pass: clarified remote capability boundaries, origin attribution, and non-parity doctrine.
- r1: Machine-readable normalization pass, unique section anchors, metadata cleanup, and content polish against the current governed corpus.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-REM-SPEC-001::1]

This document defines the canonical remote-access model for UniversalDAQ. It specifies how remote clients may observe system state, review history, supervise runtime behavior, and issue limited command requests through the backend-authoritative platform model. It also defines the boundaries between remote observation, remote supervision, and remote direct control.

This document does not define internet-facing network security implementation details, cloud deployment architecture, or vendor-specific remote desktop products. It defines the platform behavior that remote-capable deployments shall satisfy.

## 2. Scope [SEC:UDQ-REM-SPEC-001::2]

This specification applies to:

- remote observation clients
- remote supervisory clients
- backend publication of live and historical state to remote surfaces
- attribution, audit, and explainability of remote-origin actions
- multi-client visibility and ownership implications
- degraded, disconnected, and reconnect behavior for remote sessions

This specification does not grant unrestricted remote authority. All remote-origin commands remain subordinate to backend arbitration, interlocks, permissives, inhibits, output ownership, safe-state doctrine, and deployment policy.

## 2A. Semantic Closure and Anti-Conflation Rule [SEC:UDQ-REM-SPEC-001::2A]

Remote observation, supervision, and direct control are distinct capability classes. Remote surfaces shall not assume local parity unless policy explicitly grants it. Remote-origin actions shall remain attributable as remote-origin, and remote presentation shall not blur connectivity truth, latency truth, or authority limits.

## 3. Normative Principles [SEC:UDQ-REM-SPEC-001::3]

1. Remote access shall be a first-class platform capability, not an afterthought bolted onto a local-only application.
2. Remote clients shall consume backend-authoritative state and shall not establish an alternate source of truth.
3. Remote observation shall be easier to enable than remote supervision.
4. Remote supervision shall be easier to enable than remote direct control.
5. Every remote-origin command or acknowledgment shall be attributable, auditable, and visible as remote-origin.
6. A remote client shall not be permitted to bypass backend arbitration, interlocks, safe-state behavior, or deployment policy.
7. Loss of remote connectivity shall not imply loss of backend continuity.
8. Remote users shall not be allowed to confuse stale mirrored data with current applied machine state.
9. Multi-client situations shall be explicit, not hidden.
10. The system shall remain intelligible when local and remote clients are present simultaneously.

## 4. Remote Access Levels [SEC:UDQ-REM-SPEC-001::4]

### 4.1 Observation [SEC:UDQ-REM-SPEC-001::4.1]

Remote observation is read-oriented access to platform state. Observation may include:

- live value viewing
- device health viewing
- alarm/event viewing
- historical trend review
- sequence/runtime status review
- export of non-command evidence where allowed by deployment policy

A pure observation client shall not:

- issue output commands
- acknowledge alarms/events
- change persistent configuration
- edit rules, sequences, or signal definitions
- assume control ownership of any output or sequence

### 4.2 Supervision [SEC:UDQ-REM-SPEC-001::4.2]

Remote supervision is limited intervention above observation. Supervision may include, where allowed:

- alarm/event acknowledgment
- sequence start/stop/pause/reset requests
- mode-change requests
- bounded setpoint requests
- subsystem enable/disable requests
- controlled historian/export requests

Remote supervision shall remain request-based and shall be subject to backend policy, active ownership, interlocks, and safe-state doctrine.

### 4.3 Direct Control [SEC:UDQ-REM-SPEC-001::4.3]

Remote direct control is explicit remote issuance of manual or low-level output commands, including commands to physical outputs or Modbus-backed writable points.

Remote direct control shall be treated as a deployment-specific capability that may be disabled entirely. When enabled, it shall be clearly distinct from remote supervision and shall require stronger visibility, attribution, and confirmation behavior.

## 5. Canonical Remote Session Model [SEC:UDQ-REM-SPEC-001::5]

A remote-capable deployment shall represent remote participation using canonical session objects. A remote session shall minimally include:

- session identifier
- connected client identifier
- client type
- user or operator identity where available
- origin classification (`remote_observer`, `remote_supervisor`, `remote_direct_control`, `service`)
- connected timestamp
- last-seen timestamp
- requested capability level
- granted capability level
- session health/state
- active workspace or surface context where relevant

Remote sessions shall be visible to the backend and inspectable in diagnostics.

## 6. Canonical State Publication Model [SEC:UDQ-REM-SPEC-001::6]

The backend shall publish a canonical remote-consumable state model. That published model shall derive from the same authoritative state used by the local frontend and platform internals.

The published remote state shall support, as applicable:

- system-level runtime state
- device connectivity/health state
- signal values, units, quality, timestamps, and provenance
- output requested/applied/observed state where relevant
- active ownership and arbitration state
- alarm/event state and acknowledgment state
- sequence state and current step context
- historian availability state
- diagnostics/health summaries
- session and client-presence summaries

Remote publication shall distinguish between:

- live current state
- cached state
- stale mirrored state
- historical data
- simulated or service-mode state

## 7. Time, Latency, and Freshness Doctrine [SEC:UDQ-REM-SPEC-001::7]

Remote access inherently introduces delay and discontinuity. Therefore:

1. Remote surfaces shall display freshness state, not merely values.
2. Remote surfaces shall not imply sub-second certainty unless the backend actually provides it.
3. Remote command surfaces shall not assume that the displayed value is the final applied state until backend confirmation is received.
4. Remote clients shall show pending/requested/confirmed distinctions for command-bearing interactions.
5. Where latency or degradation exceeds configured thresholds, remote command affordances may be degraded, gated, or disabled by policy.

## 8. Capability and Policy Model [SEC:UDQ-REM-SPEC-001::8]

Remote access shall be constrained by a capability model. Capability shall be determined by deployment configuration and, where available, session identity.

Capability categories shall minimally include:

- observe_live
- review_history
- export_evidence
- acknowledge_events
- supervise_sequences
- request_mode_changes
- request_setpoints
- request_output_commands
- edit_configuration
- service_diagnostics

The platform shall support deployment policies that deny specific remote capabilities even when local equivalents exist.

## 9. Remote UI Requirements [SEC:UDQ-REM-SPEC-001::9]

### 9.1 Common Remote UI Obligations [SEC:UDQ-REM-SPEC-001::9.1]

Remote surfaces shall:

- visibly indicate that the session is remote
- show current freshness/latency state
- show backend connectivity state
- expose active ownership and lockouts where relevant
- distinguish observation-only from supervisory-capable sessions
- prevent hidden command issuance from purely observational surfaces

### 9.2 Remote Observation Surfaces [SEC:UDQ-REM-SPEC-001::9.2]

Observation-oriented remote views shall prioritize:

- system summary
- live trends and values
- event/alarm review
- sequence review
- historian access
- diagnostics summary

Observation surfaces should suppress or visually de-emphasize edit/command controls when those controls are unavailable.

### 9.3 Remote Supervision Surfaces [SEC:UDQ-REM-SPEC-001::9.3]

Supervisory remote views shall additionally provide:

- explicit command request controls for allowed supervisory actions
- confirmation flows where required
- pending/result feedback
- visible reasons when a request is denied, blocked, inhibited, or preempted

### 9.4 Remote Direct Control Surfaces [SEC:UDQ-REM-SPEC-001::9.4]

Where remote direct control is enabled, the UI shall make it unmistakable that the user is operating a command-capable remote surface. Such surfaces shall show:

- that the origin is remote
- ownership state
- output target identity
- requested value
- applied state when confirmed
- inhibit/interlock reasons
- safe-state and deployment-policy constraints

## 10. Remote Commands and Arbitration [SEC:UDQ-REM-SPEC-001::10]

All remote-origin commands shall be treated as command requests. No remote client shall directly mutate final output state outside backend arbitration.

A remote command request shall be evaluated against:

- capability policy
- current session state
- platform mode/state
- output ownership
- interlocks, permissives, and inhibits
- safe-state conditions
- device health/availability
- target-specific constraints

The platform shall visibly distinguish at least the following command phases:

- requested
- pending evaluation
- accepted
- rejected
- superseded
- applied
- failed to apply
- observed mismatch

## 11. Multi-Client Doctrine [SEC:UDQ-REM-SPEC-001::11]

The platform shall support simultaneous local and remote clients without silent ambiguity.

The following shall be visible where relevant:

- multiple active sessions
- which session issued the last command request
- whether a remote session currently holds supervisory or manual ownership
- whether a local user is actively operating a conflicting surface
- whether a remote request was denied due to active ownership elsewhere

Remote access shall not silently steal authority from a local or other remote user unless deployment policy explicitly defines a takeover mechanism.

## 12. Local vs Remote Ownership Semantics [SEC:UDQ-REM-SPEC-001::12]

Ownership precedence shall be determined by the platform output/arbitration model, not by UI proximity. However, the remote specification imposes the following additional obligations:

1. Origin (`local`, `remote`, `sequence`, `rule`, `safe_state`, `service`) shall be visible for active ownership.
2. Remote-origin ownership shall be explicitly labeled as remote-origin.
3. Release or timeout of remote-origin manual ownership shall be visible as an event.
4. Safe-state behavior shall preempt remote-origin ownership when required by doctrine.

## 13. Remote Review of Rules, Sequences, and Dependencies [SEC:UDQ-REM-SPEC-001::13]

Remote clients with observation capability shall be able to review the explanatory surfaces needed to understand system behavior, subject to deployment policy. This includes:

- active rule truth state and live trace where made available
- sequence state and current-step explanation
- output ownership explanation
- device health summaries
- dependency relationships necessary to explain current blocking or inhibition

Remote review shall not imply remote editing capability.

## 14. Historian and Evidence Access [SEC:UDQ-REM-SPEC-001::14]

Remote historian access shall be treated as a first-class read path. Remote review shall support:

- historical trends
- event/alarm history
- command and acknowledgment history where allowed
- sequence history where relevant
- audit/evidence export where allowed

When exporting evidence remotely, the system shall record:

- session identity/origin
- export timestamp
- export scope
- any policy-based redactions or restrictions

## 15. Degraded and Disconnected Behavior [SEC:UDQ-REM-SPEC-001::15]

### 15.1 Backend Continues Without Remote Client [SEC:UDQ-REM-SPEC-001::15.1]

Loss of a remote client shall not stop the backend or imply a local system failure.

### 15.2 Remote Client Loses Freshness [SEC:UDQ-REM-SPEC-001::15.2]

When a remote client is connected but sufficiently delayed or unable to refresh state adequately, the remote UI shall show degraded freshness. Command-capable actions may be limited or blocked by deployment policy.

### 15.3 Remote Session Drop During Active Supervision [SEC:UDQ-REM-SPEC-001::15.3]

Loss of a remote supervisory session shall not imply that unconfirmed requested actions were applied. The backend shall resolve any in-flight requests according to its normal command lifecycle and shall log the remote session loss.

### 15.4 Remote Session Drop During Remote Direct Manual Ownership [SEC:UDQ-REM-SPEC-001::15.4]

Where remote direct control is enabled, deployment policy shall define how remote-origin manual ownership is released on disconnect. Supported strategies may include:

- immediate ownership release
- timeout-based release
- hold-last-until-explicit-release
- forced safe-state transition

The chosen strategy shall be visible, documented, and audited.

## 16. Reconnect and Resume Doctrine [SEC:UDQ-REM-SPEC-001::16]

On reconnect, a remote client shall not assume that its prior local cache, prior edit buffer, or prior command context remains authoritative. The backend shall reassert current authoritative state.

Reconnected clients shall:

- refresh current state
- refresh active ownership
- refresh current sequence/runtime state
- refresh alarm/event acknowledgment state
- mark any stale pre-disconnect cached views as no longer authoritative

## 17. Diagnostics and Explainability Requirements [SEC:UDQ-REM-SPEC-001::17]

The platform shall provide remote-related diagnostics including:

- active remote sessions
- session health and last-seen time
- remote publication health
- dropped or stale update indications
- rejected command reasons
- active capability limits
- ownership conflicts involving remote sessions

Operators and engineers shall be able to determine why a remote action was or was not allowed.

## 18. Logging and Audit Requirements [SEC:UDQ-REM-SPEC-001::18]

The following shall be logged as first-class evidence where applicable:

- remote session start and end
- capability granted and denied
- command requests from remote origin
- alarm/event acknowledgment from remote origin
- mode changes initiated from remote origin
- remote export actions where policy requires auditing
- ownership acquisition/release involving remote origin
- remote-related rejection, inhibit, or denial reasons

Audit entries shall preserve origin context sufficient to distinguish remote from local activity.

## 19. Remote Configuration Boundaries [SEC:UDQ-REM-SPEC-001::19]

Remote editing of persistent configuration, such as signal definitions, rules, sequences, protocol maps, or package-governing documents, shall be treated as a stronger capability than runtime supervision.

Deployments may choose any of the following positions:

- prohibit remote persistent editing entirely
- allow remote persistent editing only in service/engineering mode
- allow remote persistent editing only on trusted network contexts

The deployment position shall be explicit rather than implicit.

## 20. Deployment Profiles [SEC:UDQ-REM-SPEC-001::20]

The platform shall support at least the following remote deployment profiles conceptually:

1. **Observe-only** — remote users may view live and historical information but cannot issue runtime actions.
2. **Supervisory** — remote users may observe and perform bounded supervisory actions.
3. **Service/Engineering** — remote users may perform extended diagnostics and, where allowed, controlled configuration tasks.
4. **Direct-control-enabled** — remote deployments that explicitly permit remote manual output requests under strict policy.

These profiles may be implemented through configuration, but the conceptual distinction shall remain visible in the platform model.

## 21. Anti-Patterns [SEC:UDQ-REM-SPEC-001::21]

The following are prohibited or strongly disfavored:

- remote UI treated as a second source of truth
- remote direct output writes bypassing backend arbitration
- stale remote data rendered as though it is current live state
- hidden ownership conflicts between local and remote clients
- remote manual control without explicit remote-origin labeling
- silent downgrade of failed remote command requests
- remote editing surfaces exposed without clear capability gating
- remote disconnection behavior that is undefined or undocumented

## 22. Verification Expectations [SEC:UDQ-REM-SPEC-001::22]

The platform shall be verifiable against this specification using evidence such as:

- session logs
- command attribution records
- ownership conflict demonstrations
- remote reconnect demonstrations
- stale/degraded-state UI demonstrations
- export/audit records
- deployment-profile configuration evidence

## 23. Downstream Implications [SEC:UDQ-REM-SPEC-001::23]

This document shall inform at least:

- requirements traceability updates for remote observation/supervision
- UI page/workspace specifications for remote-capable surfaces
- proof model and audit expectations
- output/arbitration tests involving remote-origin commands
- historian/evidence checks for remote-origin activity

## Revision History

- **r0 / WIP** — Initial controlled specification defining the canonical remote observation and supervision model, capability levels, session model, arbitration boundaries, degraded/disconnect behavior, and audit obligations.
