---
document_id: UDQ-SIG-SPEC-001
title: Signals and Derived Signals Specification
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
  - UDQ-LOG-SPEC-001
supersedes:
  - UDQ-SIG-SPEC-001__Signals_and_Derived_Signals_Specification__r0__WIP.md
---

# Signals and Derived Signals Specification [SEC:UDQ-SIG-SPEC-001::0]

## Revision History [SEC:UDQ-SIG-SPEC-001::0.1]
- r1: Machine-readable normalization pass, unique section anchors, metadata cleanup, and content polish against the current governed corpus.
- r0: Initial working issue.

## 1. Purpose [SEC:UDQ-SIG-SPEC-001::1]

This document defines the canonical signal model for UniversalDAQ. It establishes how raw measured values, imported values, device-backed states, virtual states, and derived values shall be represented, validated, published, historized, displayed, and consumed by other subsystems.

The signal model is foundational. Rules, sequences, outputs, historian behavior, diagnostics, remote publication, and UI explainability all depend on it. UniversalDAQ shall therefore treat signals as first-class platform objects rather than as ad hoc channels hidden inside device-specific integrations.

---

## 2. Scope [SEC:UDQ-SIG-SPEC-001::2]

This specification covers:
- raw acquired signals
- device-provided status/state signals
- imported protocol-backed values
- internally maintained virtual signals
- derived numeric, boolean, enum, and string signals
- signal identity, metadata, quality, and publication
- dependency behavior for derived signals
- historization expectations
- UI exposure expectations
- lifecycle and validation requirements

This specification does not fully define:
- protocol-specific addressing details
- output arbitration semantics
- sequence semantics
- historian storage implementation internals
- remote transport protocol details

Those are defined in other subsystem specifications.

---

## 3. Design Intent [SEC:UDQ-SIG-SPEC-001::3]

UniversalDAQ shall treat all values of operational interest as normalized signals. The system may acquire data through many protocol or device adapters, but downstream consumers shall work primarily with signal objects rather than raw device driver variables.

The signal system shall support two complementary goals:
1. preserving traceable connection to the originating source, and
2. making the value usable in a device-agnostic way throughout the rest of the platform.

This means a Modbus register, a LabJack analog input, a PSU measured current, a connection-health bit, a derived pressure delta, and a rule-produced virtual readiness state shall all fit into one coherent signal model, even though their sources differ.

---

## 4. Signal Categories [SEC:UDQ-SIG-SPEC-001::4]

### 4.1 Raw Signals [SEC:UDQ-SIG-SPEC-001::4.1]

A raw signal is a value directly acquired from a hardware device, protocol endpoint, software source, or external service, prior to any nontrivial logical derivation.

Examples include:
- analog input voltage
- digital input state
- measured current from an instrument
- Modbus register value after transport decode
- device online/offline heartbeat state
- serial parser output value

Raw does not necessarily mean unscaled. A transport adapter may need to perform basic decode operations required to interpret bytes, registers, or transport payloads. However, the result shall still be treated as raw if it directly represents the source point rather than a platform-level calculation.

### 4.2 Normalized Signals [SEC:UDQ-SIG-SPEC-001::4.2]

A normalized signal is the canonical platform representation of a source-backed value after minimal source interpretation, metadata assignment, and quality evaluation.

Every raw source value that is made visible to the rest of UniversalDAQ shall become a normalized signal.

### 4.3 Derived Signals [SEC:UDQ-SIG-SPEC-001::4.3]

A derived signal is computed from one or more other signals using a defined expression, transform, function, state machine, rolling operation, or aggregation.

Derived signals may be:
- numeric
- boolean
- enum/state-valued
- string-valued where justified

Derived signals shall be first-class objects with their own identity, metadata, quality state, timestamps, and dependency maps.

### 4.4 Virtual Signals [SEC:UDQ-SIG-SPEC-001::4.4]

A virtual signal is a platform-defined signal not directly tied to one physical source measurement. It may represent:
- mode
- readiness
- connectivity state
- output ownership state
- sequence state
- user/session-selected state where publication is justified

Virtual signals may be raw to the platform even if they are not raw to hardware.

### 4.5 Imported Signals [SEC:UDQ-SIG-SPEC-001::4.5]

An imported signal is a normalized signal whose source is external to the local acquisition engine, such as:
- another backend node
- remote publisher
- imported dataset replay
- supervisory system feed

Imported signals shall still conform to the same signal identity and quality model.

---

## 5. Canonical Signal Object [SEC:UDQ-SIG-SPEC-001::5]

Every signal shall have a canonical object definition containing at least the following conceptual fields.

### 5.1 Identity Fields [SEC:UDQ-SIG-SPEC-001::5.1]
- stable signal identifier
- human-readable name
- optional display name
- category/type classification
- originating source identifier
- source path or source reference
- namespace or grouping context

### 5.2 Data Fields [SEC:UDQ-SIG-SPEC-001::5.2]
- current value
- declared value type
- engineering units where applicable
- optional raw/source value representation where useful
- optional display precision metadata

### 5.3 Time Fields [SEC:UDQ-SIG-SPEC-001::5.3]
- source timestamp if available
- acquisition/receipt timestamp
- publication timestamp
- last value-change timestamp
- last quality-change timestamp

### 5.4 Quality Fields [SEC:UDQ-SIG-SPEC-001::5.4]
- validity state
- freshness/staleness state
- communication/source health state
- substitution/simulation/override indicators
- calculation status for derived signals
- explanation or reason code where available

### 5.5 Metadata Fields [SEC:UDQ-SIG-SPEC-001::5.5]
- description
- subsystem or area assignment
- tags/labels
- default visibility class
- historian eligibility/policy
- alarm or rule relevance flags where appropriate
- security/editability classification for configuration-facing signals

### 5.6 Dependency Fields [SEC:UDQ-SIG-SPEC-001::5.6]
For derived or virtual signals with dependencies:
- dependency list
- dependency revision/signature
- cycle-validation status
- calculation definition reference

This conceptual model may later be formalized in a schema specification, but all downstream systems shall behave as if these classes of information exist even if a first implementation stores them in simpler structures.

---

## 6. Signal Identity Doctrine [SEC:UDQ-SIG-SPEC-001::6]

### 6.1 Stable IDs [SEC:UDQ-SIG-SPEC-001::6.1]

Every signal shall have a stable identifier that survives ordinary restarts, UI sessions, and historian usage. Human-readable names may change, but identity for configuration, rules, historian references, and dependencies shall not depend solely on the display name.

### 6.2 Human Names vs Stable IDs [SEC:UDQ-SIG-SPEC-001::6.2]

The platform shall distinguish between:
- stable machine identity
- configured name
- optional display name or label

Rules, sequences, and dependent configurations should anchor primarily to stable identity, while the UI may prominently show configured names and aliases.

### 6.3 Namespaces and Grouping [SEC:UDQ-SIG-SPEC-001::6.3]

Signals shall support grouping constructs such as:
- device group
- protocol group
- subsystem group
- user-defined grouping
- workspace-relevant grouping

Grouping shall aid organization, not redefine identity.

### 6.4 Rename Safety [SEC:UDQ-SIG-SPEC-001::6.4]

Renaming a signal shall not silently sever valid references if the stable identity remains unchanged. The system shall preserve reference integrity wherever possible and surface any exceptions explicitly.

---

## 7. Value Types [SEC:UDQ-SIG-SPEC-001::7]

The signal model shall support, at minimum:
- boolean
- integer
- floating-point numeric
- enum/state
- string
- timestamp/duration where justified

The system shall avoid ambiguous type behavior. Comparisons, derived calculations, rule evaluations, and UI editors shall work from explicit type information rather than guessing.

### 7.1 Numeric Signals [SEC:UDQ-SIG-SPEC-001::7.1]

Numeric signals may carry:
- engineering units
- precision/display hints
- optional display range hints
- optional source/engineering scaling metadata

### 7.2 Boolean Signals [SEC:UDQ-SIG-SPEC-001::7.2]

Boolean signals shall support explicit true/false semantics and shall not rely on arbitrary numeric conventions in downstream logic.

### 7.3 Enum/State Signals [SEC:UDQ-SIG-SPEC-001::7.3]

Enum signals are preferred over free-form strings where a signal represents a bounded state set such as:
- RUN / STOP / FAULT
- AUTO / MANUAL / SAFE
- CONNECTING / ONLINE / DEGRADED / OFFLINE

### 7.4 String Signals [SEC:UDQ-SIG-SPEC-001::7.4]

String signals should be used sparingly for operational logic. They are appropriate for descriptive or diagnostic content, but rules and sequences should prefer typed values and enums.

---

## 8. Scaling and Interpretation [SEC:UDQ-SIG-SPEC-001::8]

### 8.1 Source Decode vs Engineering Conversion [SEC:UDQ-SIG-SPEC-001::8.1]

The platform shall distinguish conceptually between:
- transport or protocol decode needed to obtain the raw point value, and
- engineering conversion or interpretation used to create the operational signal value.

### 8.2 Source Value Retention [SEC:UDQ-SIG-SPEC-001::8.2]

Where useful for diagnostics or auditability, the platform should preserve the source-representative value alongside the engineering value or provide traceability back to it.

### 8.3 Unit Discipline [SEC:UDQ-SIG-SPEC-001::8.3]

Signals with physical meaning shall carry declared engineering units where applicable. Derived expressions and UI displays shall not silently assume units that are absent or ambiguous.

### 8.4 Scaling Metadata [SEC:UDQ-SIG-SPEC-001::8.4]

Signals should support metadata for:
- source range
- engineering range
- clamp information
- signedness interpretation where relevant
- precision guidance

This metadata is especially important for analog and protocol-backed numeric values.

---

## 9. Quality Model [SEC:UDQ-SIG-SPEC-001::9]

The signal model shall incorporate quality as a first-class property, not a side note.

### 9.1 Minimum Quality Dimensions [SEC:UDQ-SIG-SPEC-001::9.1]

Each signal shall carry enough quality state to determine at least:
- whether the current value is valid
- whether the value is fresh or stale
- whether the source path is healthy
- whether the value is simulated, substituted, or overridden
- whether the value is indeterminate due to dependency issues or failed calculation

### 9.2 Freshness and Staleness [SEC:UDQ-SIG-SPEC-001::9.2]

Freshness shall not be inferred solely from value change. A constant value may still be fresh if updates are arriving as expected. Likewise, an unchanged display does not mean the signal is stale.

The platform shall therefore track update-time semantics separately from value-change semantics.

### 9.3 Disconnected Sources [SEC:UDQ-SIG-SPEC-001::9.3]

When the source path becomes disconnected, the signal shall not silently continue to appear normal. The signal quality state shall explicitly indicate the loss of trust in that signal.

### 9.4 Simulation and Override [SEC:UDQ-SIG-SPEC-001::9.4]

Simulated, substituted, and manually overridden values shall be visibly and logically distinguished from ordinary live values. Downstream subsystems shall be able to detect these states programmatically.

### 9.5 Derived Quality Propagation [SEC:UDQ-SIG-SPEC-001::9.5]

Derived signal quality shall be determined from both:
- the quality of dependencies, and
- the health of the calculation itself.

Derived signals shall not silently flatten dependency-quality distinctions into a single undifferentiated state if more precise reporting is possible.

---

## 10. Timestamp Doctrine [SEC:UDQ-SIG-SPEC-001::10]

Signals shall support separation of multiple time meanings.

### 10.1 Source Timestamp [SEC:UDQ-SIG-SPEC-001::10.1]

If the originating device or upstream system provides a meaningful source timestamp, it shall be preserved where possible.

### 10.2 Receipt/Acquisition Timestamp [SEC:UDQ-SIG-SPEC-001::10.2]

The platform shall record when the backend actually obtained the value.

### 10.3 Publication Timestamp [SEC:UDQ-SIG-SPEC-001::10.3]

The platform shall record when the value entered the canonical published state for downstream consumers.

### 10.4 Change Timestamp [SEC:UDQ-SIG-SPEC-001::10.4]

The platform shall track the last time the value materially changed, separate from last-refresh time.

### 10.5 Quality Change Timestamp [SEC:UDQ-SIG-SPEC-001::10.5]

Quality state changes shall be timestamped independently from value changes.

These distinctions matter for historian behavior, rule explainability, diagnostics, and remote publication.

---

## 11. Derived Signal Model [SEC:UDQ-SIG-SPEC-001::11]

### 11.1 Derived Signals as First-Class Objects [SEC:UDQ-SIG-SPEC-001::11.1]

Derived signals shall not be treated as anonymous inline expressions scattered across the platform. If a value is important enough to be reused, historized, displayed, alarmed on, referenced by rules, or explained to a user, it shall be representable as a first-class derived signal.

### 11.2 Allowed Derived Categories [SEC:UDQ-SIG-SPEC-001::11.2]

The platform shall support derived signals created from:
- arithmetic expressions
- boolean logic
- comparisons and thresholds
- aggregates across multiple inputs
- min/max/average/select operations
- rolling window functions
- state reductions and ready/fault summaries
- explicit mappings or transforms
- conditional selection logic

### 11.3 One Canonical Model [SEC:UDQ-SIG-SPEC-001::11.3]

Derived-signal definitions shall use one canonical internal representation compatible with:
- visual builder/editor surfaces, and
- function-style textual DSL representation.

This is aligned with the same one-model/two-editor doctrine established for rules.

### 11.4 Dependency Declaration [SEC:UDQ-SIG-SPEC-001::11.4]

Every derived signal shall have an explicit dependency set. The system shall be able to determine:
- which signals feed the derived signal
- which downstream entities depend on it
- whether cycles exist
- what recalculation path is required when inputs change

### 11.5 Reuse [SEC:UDQ-SIG-SPEC-001::11.5]

Derived signals should be reusable across:
- UI displays
- historian/trends
- rules
- sequences
- diagnostics
- remote publication

The platform shall prefer reuse of named derived signals over repeated copy-pasted expressions.

---

## 12. Derived Signal Semantics [SEC:UDQ-SIG-SPEC-001::12]

### 12.1 Determinism [SEC:UDQ-SIG-SPEC-001::12.1]

Given the same dependency states and values, a derived-signal definition shall evaluate deterministically.

### 12.2 Type Predictability [SEC:UDQ-SIG-SPEC-001::12.2]

A derived signal shall declare or infer a stable output type. The system shall validate that the derivation is compatible with that type.

### 12.3 Quality-Aware Semantics [SEC:UDQ-SIG-SPEC-001::12.3]

Derived expressions shall define behavior when dependencies are:
- invalid
- stale
- offline
- simulated
- absent

The system shall not hide these cases behind ordinary numeric output unless the derivation explicitly specifies a justified fallback behavior.

### 12.4 Indeterminate States [SEC:UDQ-SIG-SPEC-001::12.4]

Some derived expressions may become indeterminate rather than simply false or zero when inputs are unusable. The platform shall support that distinction where appropriate.

### 12.5 Rolling and Stateful Calculations [SEC:UDQ-SIG-SPEC-001::12.5]

If the platform supports rolling averages, filters, edge detection, timers, or stateful transforms as derived signals, the configuration and explainability model shall indicate that such signals have memory or history dependence.

---

## 13. Dependency and Cycle Management [SEC:UDQ-SIG-SPEC-001::13]

### 13.1 Directed Dependency Graph [SEC:UDQ-SIG-SPEC-001::13.1]

The backend shall be able to model dependencies between signals as a directed graph.

### 13.2 Cycle Detection [SEC:UDQ-SIG-SPEC-001::13.2]

Configurations that introduce cycles in derived-signal dependencies shall be rejected, quarantined, or clearly disabled pending correction. UniversalDAQ shall not permit hidden circular dependencies to enter runtime silently.

### 13.3 Change Impact Visibility [SEC:UDQ-SIG-SPEC-001::13.3]

The platform should be able to answer:
- what depends on this signal
- what upstream signals feed this value
- what rules, sequences, or outputs are affected if this signal changes or fails

This capability is important for diagnostics and safe engineering changes.

### 13.4 Incremental Recalculation [SEC:UDQ-SIG-SPEC-001::13.4]

Where feasible, the backend should recalculate derived signals incrementally based on dependency changes rather than blindly reevaluating everything all the time. However, correctness and transparency are more important than premature micro-optimization.

---

## 14. Signal Lifecycle [SEC:UDQ-SIG-SPEC-001::14]

### 14.1 Definition Lifecycle [SEC:UDQ-SIG-SPEC-001::14.1]

A signal may pass through lifecycle states such as:
- defined but not yet bound
- configured and bindable
- active and publishing
- degraded
- disabled
- retired/obsolete

### 14.2 Runtime Value Lifecycle [SEC:UDQ-SIG-SPEC-001::14.2]

At runtime, a signal value may move through states such as:
- unavailable
- pending first value
- live and healthy
- live but stale
- invalid
- substituted/simulated
- offline due to source loss

### 14.3 Startup Behavior [SEC:UDQ-SIG-SPEC-001::14.3]

At startup, the system shall avoid presenting a signal as trustworthy before acquisition, import, or calculation has actually produced a valid state.

### 14.4 Reconnect Behavior [SEC:UDQ-SIG-SPEC-001::14.4]

When a source reconnects, the platform shall transition the signal back to healthy state only when the source path and the signal update stream truly recover.

---

## 15. Historian Expectations [SEC:UDQ-SIG-SPEC-001::15]

### 15.1 Historian Eligibility [SEC:UDQ-SIG-SPEC-001::15.1]

Signals should carry policy indicating whether they are eligible for historization, and if so, under what conditions.

### 15.2 Derived Signal Historization [SEC:UDQ-SIG-SPEC-001::15.2]

Derived signals may be historized directly when operationally useful. The platform should not require users to reconstruct every important derived quantity only after the fact if it is intended to be a first-class runtime quantity.

### 15.3 Quality in History [SEC:UDQ-SIG-SPEC-001::15.3]

Historian records shall preserve enough quality context to avoid replaying all values as if they were equally healthy and live.

### 15.4 Identity Stability for History [SEC:UDQ-SIG-SPEC-001::15.4]

Historian continuity shall depend on stable signal identity, not just display naming.

---

## 16. UI Exposure Doctrine [SEC:UDQ-SIG-SPEC-001::16]

### 16.1 Signals as the Primary User-Facing Abstraction [SEC:UDQ-SIG-SPEC-001::16.1]

Normal users should interact primarily with signals and logical points, not low-level device driver internals.

### 16.2 Required Signal Visibility [SEC:UDQ-SIG-SPEC-001::16.2]

The UI architecture shall be able to present at least:
- current value
- name/display label
- type and units where applicable
- quality/freshness state
- source grouping
- last update/change timing
- derived/raw distinction where meaningful

### 16.3 Derived Signal Explainability [SEC:UDQ-SIG-SPEC-001::16.3]

For derived signals, the UI shall support inspection of:
- the calculation definition
- current dependency values
- dependency quality states
- the resulting evaluation state
- last change reason where feasible

### 16.4 Edit Surfaces [SEC:UDQ-SIG-SPEC-001::16.4]

The UI should support both:
- structured visual editing of derived signals, and
- function-style DSL editing,
using a shared canonical representation.

### 16.5 Search, Filter, and Grouping [SEC:UDQ-SIG-SPEC-001::16.5]

As signal counts grow, the UI shall support practical organization by device, subsystem, type, protocol, tags, favorites, or other grouping concepts.

---

## 17. Relationship to Rules and Sequences [SEC:UDQ-SIG-SPEC-001::17]

### 17.1 Signals as Rule Inputs [SEC:UDQ-SIG-SPEC-001::17.1]

Rules shall consume signals, not ad hoc device variables. This includes raw, derived, and virtual signals.

### 17.2 Derived Signals vs Inline Rule Expressions [SEC:UDQ-SIG-SPEC-001::17.2]

If logic is reused, operationally meaningful, or likely to need display/history/diagnostic value outside a single rule, it should become a named derived signal rather than remain buried inside one rule expression.

### 17.3 Signals as Sequence Conditions [SEC:UDQ-SIG-SPEC-001::17.3]

Sequences should use signal references for entry conditions, step conditions, termination conditions, and fault conditions.

### 17.4 Signals as Published Contract [SEC:UDQ-SIG-SPEC-001::17.4]

Signals form part of the contract between backend, UI, historian, remote observers, and control logic. They are therefore a shared platform language.

---

## 18. Relationship to Outputs and Commands [SEC:UDQ-SIG-SPEC-001::18]

Signals may represent output feedback, command state, ownership state, permissive state, and other output-related information, but signal publication shall remain distinct from action authority.

In other words:
- a signal may indicate that an output request exists,
- a signal may indicate that an output is currently active,
- a signal may indicate which subsystem owns that output,

but the signal model itself shall not replace command arbitration logic.

---

## 19. Validation Requirements [SEC:UDQ-SIG-SPEC-001::19]

Before a signal definition or derived-signal definition becomes active, the platform shall validate at least:
- identifier uniqueness
- type consistency
- unit plausibility where applicable
- source binding integrity for raw/imported signals
- dependency existence for derived signals
- absence of prohibited cycles
- compatibility of declared calculation functions and operands
- historian policy validity
- UI/display configuration sanity where required

Validation failures shall be visible and explainable.

---

## 20. Anti-Patterns [SEC:UDQ-SIG-SPEC-001::20]

The platform shall avoid the following anti-patterns:
- treating device-specific variables as the de facto platform signal model
- using display names as the only durable identity
- flattening freshness and validity into one ambiguous flag
- hiding simulated or substituted values behind ordinary live presentation
- duplicating the same derived calculation in many places rather than creating one named signal
- allowing silent dependency cycles
- making signal quality unavailable to rules or UI logic
- making historian continuity depend on unstable labels

---

## 21. Minimum Implementation Phasing Guidance [SEC:UDQ-SIG-SPEC-001::21]

### Phase 1
- canonical normalized signal object for raw/live values
- stable IDs and names
- basic type support
- basic quality and timestamp handling
- signal browser/UI exposure
- historian linkage by stable identity

### Phase 2
- first-class derived signals
- visual builder and function-style DSL for derived-signal definitions
- dependency graph and cycle detection
- derived signal inspectability in UI

### Phase 3
- richer aggregates and rolling/stateful derivations
- advanced impact analysis and cross-reference views
- more sophisticated remote publication and dependency explanation surfaces

Phasing may vary, but later phases shall not invalidate the core doctrine established here.

---

## 22. Downstream Obligations [SEC:UDQ-SIG-SPEC-001::22]

This specification shall feed updates or detailed implementations in:
- requirements traceability rows for signals, derivations, historian, UI explainability, and remote publication
- definition-of-complete criteria for signal subsystem maturity
- rule engine implementation and validation behavior
- output/arbitration visibility models
- Modbus and protocol integration specifications
- historian and event specifications
- UI workspace specifications for Signals and Diagnostics

---

## 23. Summary [SEC:UDQ-SIG-SPEC-001::23]

UniversalDAQ shall treat signals as the canonical operational language of the platform. Raw measurements, imported values, platform states, and derived quantities shall all become coherent first-class signal objects with durable identity, clear typing, explicit quality, timestamp discipline, dependency visibility, and reusable value across UI, rules, sequences, historian, diagnostics, and remote publication.

Derived signals shall not be second-class expressions hidden in isolated logic blocks. They shall be publishable, inspectable, historizable, and editable through one canonical model that supports both visual and function-style textual editing.

This specification establishes the stable substrate on which rules, outputs, Modbus integration, and broader UniversalDAQ platform behavior can be built.
