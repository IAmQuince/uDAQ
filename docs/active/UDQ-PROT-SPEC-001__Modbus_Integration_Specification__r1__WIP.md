---
document_id: UDQ-PROT-SPEC-001
title: Modbus Integration Specification
revision: r1
status: WIP
document_class: subsystem_spec
owner: UniversalDAQ
depends_on:
  - UDQ-ARCH-NAR-001
  - UDQ-ARCH-NAR-002
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-MOD-001
  - UDQ-SIG-SPEC-001
  - UDQ-LOG-SPEC-001
  - UDQ-OUT-SPEC-001
supersedes:
  - UDQ-PROT-SPEC-001__Modbus_Integration_Specification__r0__WIP.md
---

# Modbus Integration Specification [SEC:UDQ-PROT-SPEC-001::0]

## Revision History [SEC:UDQ-PROT-SPEC-001::0.1]
- r1: Machine-readable normalization pass, unique section anchors, metadata cleanup, and content polish against the current governed corpus.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-PROT-SPEC-001::1]

This document defines how Modbus shall be represented, configured, polled, decoded, written, monitored, diagnosed, and surfaced within UniversalDAQ.

The purpose of this specification is to make Modbus a first-class protocol integration rather than a special-case bolt-on. Modbus devices, points, transactions, health states, and writable capabilities shall fit into the same canonical platform model used by signals, outputs, rules, sequences, historian, diagnostics, and remote supervision.

This document does **not** define implementation code, wire-level optimization details, or vendor-specific maps. It defines the system-level obligations and canonical model that later schemas, UI specs, tests, and implementation must follow.

---

## 2. Scope [SEC:UDQ-PROT-SPEC-001::2]

This specification applies to:

- Modbus TCP client integrations.
- Modbus RTU client integrations.
- devices polled by UniversalDAQ.
- writable Modbus-backed outputs controlled through UniversalDAQ arbitration.
- the transformation of raw Modbus points into canonical UniversalDAQ signals and outputs.
- communication health, timeout, stale, invalid, and fault handling for Modbus-connected devices.
- configuration, diagnostics, historian implications, UI exposure, and remote supervision consequences.

This specification does not currently cover:

- UniversalDAQ acting as a Modbus server/slave.
- gateway product selection or external network design.
- vendor-specific commissioning procedures.
- safety certification or regulatory qualification outside the platform control model.

---

## 3. Design Principles [SEC:UDQ-PROT-SPEC-001::3]

### 3.1 First-Class Protocol Principle [SEC:UDQ-PROT-SPEC-001::3.1]

Modbus shall be treated as a first-class protocol family within UniversalDAQ. It shall not be relegated to ad hoc register reads outside the device, signal, output, and diagnostics model.

### 3.2 Canonical Representation Principle [SEC:UDQ-PROT-SPEC-001::3.2]

Raw Modbus addresses, coils, registers, byte ordering decisions, and protocol exceptions shall be translated into canonical platform objects. Everyday operator workflows shall primarily interact with named devices, signals, statuses, and outputs rather than raw register numbers.

### 3.3 Backend Authority Principle [SEC:UDQ-PROT-SPEC-001::3.3]

All Modbus communication state, decoded values, write requests, write outcomes, health conditions, and quality states shall be backend-authoritative. Frontends may configure, inspect, and request actions, but they shall not become the source of truth.

### 3.4 Quality Truthfulness Principle [SEC:UDQ-PROT-SPEC-001::3.4]

Timeouts, exception responses, stale data, decode failures, conflicting type assumptions, write failures, and communication degradation shall be represented honestly and visibly. Missing or degraded Modbus data shall not silently masquerade as good live values.

### 3.5 Separation of Concerns Principle [SEC:UDQ-PROT-SPEC-001::3.5]

Modbus communication mechanics shall be separated from:

- signal semantics,
- rule semantics,
- output arbitration,
- UI rendering,
- historian storage policy,
- and remote publication.

Modbus provides raw and decoded point values plus writable capabilities; the rest of the platform interprets those through canonical platform models.

### 3.6 Explainability Principle [SEC:UDQ-PROT-SPEC-001::3.6]

Users shall be able to understand:

- what device a value came from,
- what raw point produced it,
- how it was decoded,
- when it was last updated,
- whether it is fresh, stale, invalid, or faulted,
- whether a write was requested, applied, rejected, timed out, or blocked,
- and what communication health state currently exists.

---

## 4. Conceptual Model [SEC:UDQ-PROT-SPEC-001::4]

UniversalDAQ shall model Modbus integrations using the following conceptual layers.

### 4.1 Transport / Session Layer [SEC:UDQ-PROT-SPEC-001::4.1]

Represents the communication channel used to reach the device.

Examples:
- TCP socket to IP/port.
- RTU serial line over COM port with baud/parity/stop-bit settings.

### 4.2 Device Layer [SEC:UDQ-PROT-SPEC-001::4.2]

Represents a specific Modbus target device.

A device is the canonical owning object for:
- identity,
- connection/session settings,
- unit/slave address,
- health state,
- polling groups,
- point map,
- writable capabilities,
- diagnostics,
- and device-level metadata.

### 4.3 Point Layer [SEC:UDQ-PROT-SPEC-001::4.3]

Represents the raw addressable Modbus entities defined for the device.

Examples:
- coils,
- discrete inputs,
- input registers,
- holding registers.

A point is still protocol-oriented and may not yet be suitable for normal operator use.

### 4.4 Decoded Field Layer [SEC:UDQ-PROT-SPEC-001::4.4]

Represents protocol data transformed into typed values.

Examples:
- UINT16,
- INT16,
- UINT32,
- FLOAT32,
- packed bitfields,
- enums,
- booleans,
- strings where explicitly supported.

Decoded fields bridge from raw protocol structures to platform signal/output semantics.

### 4.5 Canonical Signal / Output Layer [SEC:UDQ-PROT-SPEC-001::4.5]

Represents the UniversalDAQ-facing named entities used by rules, historian, trends, outputs, sequences, diagnostics, and remote publication.

A Modbus-backed measurement shall generally become a canonical signal. A Modbus-writable control point shall generally become a canonical output or writable capability bound to a canonical output object.

---

## 5. Supported Integration Modes [SEC:UDQ-PROT-SPEC-001::5]

### 5.1 Modbus TCP [SEC:UDQ-PROT-SPEC-001::5.1]

UniversalDAQ shall support Modbus TCP as a first-class client mode.

Configuration shall include at minimum:
- hostname or IP address,
- TCP port,
- timeout settings,
- reconnect strategy,
- unit identifier where needed,
- polling configuration,
- write enable policy,
- and device metadata.

### 5.2 Modbus RTU [SEC:UDQ-PROT-SPEC-001::5.2]

UniversalDAQ shall support Modbus RTU as a first-class client mode.

Configuration shall include at minimum:
- serial port identifier,
- baud rate,
- parity,
- stop bits,
- byte size where applicable,
- device/slave address,
- timeout settings,
- polling configuration,
- write enable policy,
- and device metadata.

### 5.3 Future Extensibility [SEC:UDQ-PROT-SPEC-001::5.3]

The platform model shall not assume that all Modbus devices behave identically. The integration architecture shall allow future support for:
- vendor-specific quirks,
- gateway-backed device fleets,
- device templates,
- replicated device classes,
- and later server/slave roles if deliberately added.

---

## 6. Canonical Device Object Requirements [SEC:UDQ-PROT-SPEC-001::6]

Each Modbus device shall have a canonical device object containing at minimum:

- stable internal device identifier,
- human-readable name,
- protocol mode (TCP or RTU),
- endpoint settings,
- unit/slave address,
- enable/disable state,
- configured polling groups,
- configured point map,
- writable capability declarations,
- communication health state,
- last successful communication timestamp,
- last failure timestamp,
- timeout and retry policy,
- diagnostics counters,
- notes / metadata,
- and provenance/config revision context.

### 6.1 Identity Stability [SEC:UDQ-PROT-SPEC-001::6.1]

A device's internal identity shall be stable across renames. Human-readable names may change without destroying historical linkage or dependencies.

### 6.2 Template Compatibility [SEC:UDQ-PROT-SPEC-001::6.2]

A device may optionally be instantiated from a reusable template, but template use shall not remove the ability to inspect and override concrete configuration fields.

### 6.3 Enable / Disable Semantics [SEC:UDQ-PROT-SPEC-001::6.3]

Disabling a Modbus device shall:
- stop active polling for that device,
- inhibit write attempts to that device,
- mark affected signals/outputs according to platform quality/state rules,
- and generate visible diagnostics/event context.

---

## 7. Point Model Requirements [SEC:UDQ-PROT-SPEC-001::7]

### 7.1 Point Categories [SEC:UDQ-PROT-SPEC-001::7.1]

The specification shall support the canonical Modbus point categories:
- Coil,
- Discrete Input,
- Input Register,
- Holding Register.

### 7.2 Point Definition Fields [SEC:UDQ-PROT-SPEC-001::7.2]

Each point definition shall support at minimum:
- stable internal point identifier,
- parent device reference,
- point category,
- starting address,
- quantity/width where applicable,
- read capability,
- write capability where applicable,
- decode type,
- byte order,
- word order,
- scaling metadata,
- engineering units metadata,
- enum/bitfield mapping where applicable,
- quality mapping behavior,
- notes,
- and UI exposure policy.

### 7.3 Read vs Write Semantics [SEC:UDQ-PROT-SPEC-001::7.3]

A point's write capability shall be explicit and shall not be inferred solely from category. A holding register is not automatically treated as writable in the platform just because Modbus allows that function in general.

### 7.4 Raw Address Truthfulness [SEC:UDQ-PROT-SPEC-001::7.4]

The system shall preserve raw protocol addressing accurately for diagnostics, testing, and service use. However, raw addresses shall not be the primary operator-facing identity in normal runtime workflows.

---

## 8. Polling and Transaction Model [SEC:UDQ-PROT-SPEC-001::8]

### 8.1 Poll Group Requirement [SEC:UDQ-PROT-SPEC-001::8.1]

UniversalDAQ shall support explicit polling groups rather than assuming that every point is individually polled on the same schedule.

A poll group shall define at minimum:
- parent device,
- function/read category,
- start address,
- quantity,
- interval / cadence,
- timeout behavior,
- retry policy,
- enable/disable state,
- decode membership,
- and diagnostics counters.

### 8.2 Grouping Principle [SEC:UDQ-PROT-SPEC-001::8.2]

Points should be grouped intentionally for efficiency and coherency, but grouping shall not erase individual field quality or decode traceability.

### 8.3 Poll Cadence Classes [SEC:UDQ-PROT-SPEC-001::8.3]

The platform should support different cadence classes, for example:
- fast runtime points,
- standard status points,
- slow configuration/status points,
- service-only points.

### 8.4 Poll Failure Semantics [SEC:UDQ-PROT-SPEC-001::8.4]

A failed poll group transaction shall not silently preserve indefinite "good" status. The platform shall update communication and data-quality state according to stale/timeout rules.

### 8.5 Partial Decode Failure [SEC:UDQ-PROT-SPEC-001::8.5]

If a poll transaction succeeds but one or more decoded fields fail due to decode assumptions, mapping errors, or incompatible width/order interpretation, those decoded fields shall be marked accordingly without forcing unrelated fields from the same transaction to become automatically invalid if they remain decodable.

---

## 9. Decode Model Requirements [SEC:UDQ-PROT-SPEC-001::9]

### 9.1 Decode as Explicit Configuration [SEC:UDQ-PROT-SPEC-001::9.1]

Every multi-register or typed interpretation beyond raw native Modbus bit/register semantics shall be explicitly configured.

The platform shall not rely on undocumented implicit assumptions for:
- signed vs unsigned interpretation,
- word order,
- byte order,
- float decoding,
- enum interpretation,
- or bitfield semantics.

### 9.2 Supported Decode Families [SEC:UDQ-PROT-SPEC-001::9.2]

The specification shall anticipate support for at least:
- BOOL,
- UINT16,
- INT16,
- UINT32,
- INT32,
- FLOAT32,
- optionally FLOAT64 where justified,
- enum mappings,
- bitfield extraction,
- simple packed status extraction,
- scaled numeric transforms,
- text/string fields only when explicitly defined and justified.

### 9.3 Scaling Model [SEC:UDQ-PROT-SPEC-001::9.3]

Scaling shall be explicit, reviewable, and separate from raw decoding.

Examples:
- raw integer to engineering units,
- linear offset/gain,
- enum mapping to platform state strings,
- bit extraction to boolean signals.

### 9.4 Decode Provenance [SEC:UDQ-PROT-SPEC-001::9.4]

The platform shall preserve enough provenance for a user or diagnostic tool to determine:
- what raw point(s) were used,
- what decode type was applied,
- what ordering/scaling assumptions were used,
- and what resulting canonical value was produced.

---

## 10. Communication Health Model [SEC:UDQ-PROT-SPEC-001::10]

### 10.1 Required Health States [SEC:UDQ-PROT-SPEC-001::10.1]

Each Modbus device shall expose explicit communication health state such as:
- disabled,
- never connected,
- connecting,
- healthy,
- degraded,
- timeout,
- communication fault,
- configuration invalid,
- and write-inhibited where relevant.

Exact naming may later be normalized, but the distinction shall exist.

### 10.2 Health Metrics [SEC:UDQ-PROT-SPEC-001::10.2]

At minimum, diagnostics should track:
- successful poll count,
- failed poll count,
- consecutive failure count,
- last successful communication time,
- last failed communication time,
- last exception code,
- reconnect attempts,
- average or representative response timing,
- write success count,
- write failure count,
- and active stale duration where relevant.

### 10.3 Health Propagation [SEC:UDQ-PROT-SPEC-001::10.3]

Device communication health shall propagate into affected point/signal/output quality state according to platform rules. The propagation shall be honest but not over-broad.

### 10.4 Distinguish Device Fault from Value Fault [SEC:UDQ-PROT-SPEC-001::10.4]

The system shall distinguish:
- communication inability to reach the device,
- exception response from the device,
- successful read with semantically invalid value,
- and decode/configuration mismatch inside UniversalDAQ.

---

## 11. Signal Integration Requirements [SEC:UDQ-PROT-SPEC-001::11]

### 11.1 Canonical Signal Creation [SEC:UDQ-PROT-SPEC-001::11.1]

Readable Modbus data that is intended for use in trends, rules, UI, historian, alarms, sequences, or remote publication shall be represented as canonical signals under UDQ-SIG-SPEC-001.

### 11.2 Metadata Preservation [SEC:UDQ-PROT-SPEC-001::11.2]

A Modbus-backed signal shall retain metadata linking it to:
- parent device,
- source point(s),
- decode configuration,
- last update timestamp,
- quality state,
- and provenance details.

### 11.3 Quality Mapping [SEC:UDQ-PROT-SPEC-001::11.3]

Signal quality shall reflect both protocol health and decode validity. A signal shall not be marked fully good merely because a value exists in memory.

### 11.4 Historian Eligibility [SEC:UDQ-PROT-SPEC-001::11.4]

Historian eligibility for Modbus-backed signals shall follow the same policy framework as other signals. Modbus origin alone shall not exclude a signal from historian use.

---

## 12. Output and Write Integration Requirements [SEC:UDQ-PROT-SPEC-001::12]

### 12.1 Write Requests as Requests [SEC:UDQ-PROT-SPEC-001::12.1]

All Modbus writes shall enter the system through the canonical output/request/arbitration model defined in UDQ-OUT-SPEC-001.

A frontend, rule, sequence, or remote client may request that a Modbus-backed output change state or value. The backend shall determine whether the request is permitted, owned, safe, and executable before attempting a Modbus write.

### 12.2 Writable Capability Declaration [SEC:UDQ-PROT-SPEC-001::12.2]

A writable Modbus target shall be declared explicitly. The platform shall know:
- what point is written,
- what type/value range is valid,
- what ownership model applies,
- whether read-back exists,
- and what safe-state behavior is required.

### 12.3 Read-Back Distinction [SEC:UDQ-PROT-SPEC-001::12.3]

Where possible, the platform shall distinguish:
- requested state/value,
- issued write payload,
- acknowledged write success/failure,
- and observed read-back state/value.

### 12.4 Write Failure Semantics [SEC:UDQ-PROT-SPEC-001::12.4]

Failed writes shall be visible. The platform shall not silently claim that a state changed merely because a request was issued.

### 12.5 Write Inhibit Conditions [SEC:UDQ-PROT-SPEC-001::12.5]

Modbus writes may be inhibited by:
- safe-state entry,
- lost communication,
- device disablement,
- output ownership conflict,
- interlock/permissive failure,
- configuration invalidity,
- deployment policy,
- remote-control restriction,
- or explicit write disable policy.

The UI and diagnostics surfaces shall expose the reason.

---

## 13. Safe-State Interaction [SEC:UDQ-PROT-SPEC-001::13]

### 13.1 Safe-State Compatibility Requirement [SEC:UDQ-PROT-SPEC-001::13.1]

For writable Modbus-backed outputs, safe-state expectations shall be explicitly defined. The platform shall not assume that the device’s last value or transport disappearance is itself safe.

### 13.2 Safe-State Modes [SEC:UDQ-PROT-SPEC-001::13.2]

At minimum, configuration should anticipate distinctions such as:
- write explicit safe value on safe-state entry,
- inhibit further writes and flag unsafe unknown,
- hold last command but mark unverified,
- or device-specific policy where justified and documented.

### 13.3 Startup and Reconnect Behavior [SEC:UDQ-PROT-SPEC-001::13.3]

On startup or reconnect, the platform shall not blindly reassert previous writes unless policy explicitly requires that and the action is validated against current mode, ownership, and safe-state rules.

---

## 14. UI Exposure Requirements [SEC:UDQ-PROT-SPEC-001::14]

### 14.1 Ordinary Operator View [SEC:UDQ-PROT-SPEC-001::14.1]

Normal runtime users should primarily see:
- device names,
- signal names,
- statuses,
- writable outputs,
- health indicators,
- alarms/events,
- and provenance summaries where needed.

They should not need to navigate raw register maps for ordinary operation.

### 14.2 Engineering / Service View [SEC:UDQ-PROT-SPEC-001::14.2]

The UI shall provide an advanced/service view exposing protocol-level details such as:
- raw point definitions,
- addresses,
- categories,
- decode settings,
- poll groups,
- timestamps,
- exception details,
- and diagnostics counters.

### 14.3 Configuration Workspace Requirement [SEC:UDQ-PROT-SPEC-001::14.3]

The device/protocol configuration workspace shall support at minimum:
- adding/editing/removing Modbus devices,
- selecting TCP vs RTU,
- configuring transport/session fields,
- defining point maps,
- defining polling groups,
- defining writable capabilities,
- testing connectivity,
- validating configuration,
- and previewing decoded point behavior.

### 14.4 Explainability Requirement [SEC:UDQ-PROT-SPEC-001::14.4]

From a canonical signal or output, the UI shall make it possible to trace back to the originating Modbus configuration and current health state.

---

## 15. Historian, Events, and Audit Requirements [SEC:UDQ-PROT-SPEC-001::15]

### 15.1 Historian Policy [SEC:UDQ-PROT-SPEC-001::15.1]

Historian treatment of Modbus-backed signals shall follow canonical signal policy. When historian storage is enabled, records shall retain timestamps and quality context sufficient for later interpretation.

### 15.2 Event Generation [SEC:UDQ-PROT-SPEC-001::15.2]

The platform should generate events for significant Modbus integration transitions, including:
- device became healthy,
- device entered degraded/faulted state,
- repeated timeout threshold crossed,
- configuration invalidation,
- write succeeded/failed where such auditing is required,
- and communication restored.

### 15.3 Audit Trail for Writes [SEC:UDQ-PROT-SPEC-001::15.3]

Where Modbus-backed outputs are writable, auditability shall include at least:
- request origin,
- requested value/state,
- arbitration result,
- whether a write was attempted,
- write success/failure,
- and observed read-back where available.

---

## 16. Remote Observation and Supervision Implications [SEC:UDQ-PROT-SPEC-001::16]

### 16.1 Remote Observation [SEC:UDQ-PROT-SPEC-001::16.1]

Remote clients may observe Modbus-backed signals and health states through canonical publication. They shall not bypass platform truth by polling Modbus devices independently under the normal platform model.

### 16.2 Remote Supervision [SEC:UDQ-PROT-SPEC-001::16.2]

Remote supervision requests affecting Modbus-backed outputs shall pass through the same arbitration and write-inhibit model as local UI requests.

### 16.3 Attribution Requirement [SEC:UDQ-PROT-SPEC-001::16.3]

The platform shall preserve the origin of remote requests so that later diagnostics and audit can distinguish:
- local operator,
- remote supervisor,
- rule engine,
- sequence engine,
- or service action.

---

## 17. Validation Requirements [SEC:UDQ-PROT-SPEC-001::17]

### 17.1 Configuration Validation [SEC:UDQ-PROT-SPEC-001::17.1]

Before activation, Modbus configuration shall be validated for at minimum:
- transport/session completeness,
- duplicate/conflicting point definitions,
- unsupported decode types,
- invalid width/order combinations,
- writable point conflicts,
- out-of-range address definitions,
- impossible poll group definitions,
- and unresolved references to canonical signals/outputs.

### 17.2 Runtime Validation [SEC:UDQ-PROT-SPEC-001::17.2]

At runtime, the platform should detect and expose:
- persistent exception responses,
- repeated decode failures,
- stale growth,
- impossible read-back states,
- unsupported value ranges,
- and configuration drift where detectable.

### 17.3 Test/Commissioning Support [SEC:UDQ-PROT-SPEC-001::17.3]

The platform shall support a practical validation workflow for commissioning, including:
- connectivity test,
- poll test,
- decode preview,
- writable capability test where safe,
- and visible diagnostics for timing and failure causes.

---

## 18. Anti-Patterns [SEC:UDQ-PROT-SPEC-001::18]

The following are explicitly disallowed architectural directions:

- Treating Modbus as ad hoc raw register polling outside the canonical device/signal/output model.
- Allowing frontends to become the source of truth for Modbus values or writes.
- Treating every holding register as writable by default.
- Hiding timeout or stale states behind the last successful numeric value.
- Making operator workflows depend primarily on raw register addresses.
- Performing uncontrolled direct writes that bypass output arbitration and safe-state policy.
- Collapsing communication fault, decode fault, and semantic value fault into one indistinct error bucket.
- Assuming one device template or one vendor byte/word ordering is universal.
- Letting historian or UI layers infer protocol meaning without explicit backend decode configuration.

---

## 19. Downstream Specification Obligations [SEC:UDQ-PROT-SPEC-001::19]

This document requires later creation of more detailed documents or schemas for at least:

1. **Modbus device configuration schema**  
   Exact fields, types, defaults, and validation rules.

2. **Modbus point/field map schema**  
   Exact representation for categories, addresses, widths, decode types, order, scaling, enum mappings, and exposure policy.

3. **Modbus diagnostics and commissioning procedure**  
   How protocol integrations are validated and evidenced during commissioning.

4. **UI workspace/page specification**  
   Exact user workflows and editing surfaces for Modbus devices, point maps, tests, health, and diagnostics.

5. **Verification and proof model updates**  
   Evidence needed to claim protocol integration completeness and release readiness.

---

## 20. Implementation Phasing Guidance [SEC:UDQ-PROT-SPEC-001::20]

### Phase A — Foundational Read Path

Initial implementation may focus on:
- Modbus TCP/RTU client connectivity,
- device objects,
- polling groups,
- decoded read-path points,
- canonical signals,
- health/timeout state,
- and diagnostic visibility.

### Phase B — Writable Integration

Next implementation may add:
- writable capability declarations,
- canonical output binding,
- arbitration-aware writes,
- read-back distinction,
- and audit trail.

### Phase C — Advanced Templates and Service Features

Later implementation may add:
- reusable device templates,
- bitfield/enum authoring helpers,
- bulk import/export,
- vendor-specific helpers,
- enhanced protocol diagnostics,
- and broader deployment tooling.

Phasing shall not violate the canonical model. Temporary implementation shortcuts shall not redefine the architecture.

---

## 21. Summary [SEC:UDQ-PROT-SPEC-001::21]

UniversalDAQ shall integrate Modbus as a first-class protocol family through canonical device, point, signal, output, health, and diagnostics models. Raw Modbus details shall remain visible for engineering and service work, but ordinary operation shall be centered on named devices, canonical signals, canonical outputs, and honest health/quality state.

All writes shall be backend-arbitrated requests, not uncontrolled direct protocol actions. All reads and writes shall carry clear provenance, quality, diagnostics, and explainability. Modbus shall fit into the same truth model as the rest of UniversalDAQ rather than existing as a parallel exception-driven subsystem.
