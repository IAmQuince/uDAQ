---
document_id: UDQ-DEV-SPEC-001
title: Device Adapter and Protocol Abstraction Specification
revision: r1
status: WIP
classification:
  domain: DEV
  type: SPEC
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-DIAG-SPEC-001
- UDQ-GOV-STD-001
- UDQ-OUT-SPEC-001
- UDQ-PROT-SPEC-001
- UDQ-SIG-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
audit_exceptions: []
---
# Device Adapter and Protocol Abstraction Specification

The current bounded package additionally treats discovery, reconciliation, polling, and command handoff as measurable hot-path seams governed by `UDQ-PERF-SPEC-001`.

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r1 | 2026-03-27 | WIP | Global documentation reconciliation: clarified cross-device read/write adapter boundaries, canonical tag/command projection, and explicit anti-contamination rules for the bounded mixed-source lanes. |
| r0 | 2026-03-21 | WIP | Initial issue defining the generalized device-adapter model above specific transport/protocol implementations. |

# 1. Purpose [SEC:UDQ-DEV-SPEC-001::1]

This specification defines how UniversalDAQ shall abstract heterogeneous devices and protocols into a common governed integration model.

# 2. Scope [SEC:UDQ-DEV-SPEC-001::2]

This specification applies to:

- device identity and lifecycle
- protocol/transport separation
- adapter responsibilities and capability declaration
- signal/output publication from adapters
- health/diagnostic integration
- configuration, validation, and evidence obligations


# 2A. Current bounded implementation note [SEC:UDQ-DEV-SPEC-001::2A]

The current bounded package now includes:
- canonical cross-device read-side tags projected from Arduino, LabJack, and Raspberry Pi specimen adapters,
- a bounded mixed-source acquisition broker for simultaneous ingest,
- a bounded write-side command/arbitration slice that still routes through canonical contracts rather than device-specific core logic.

This specification therefore now governs both read-side and first-form write-side adapter behavior for the active bounded package. It still does not authorize broad hardware generalization or device-specific leakage into the core.

# 3. Canonical abstraction layers [SEC:UDQ-DEV-SPEC-001::3]

UniversalDAQ shall distinguish at minimum:

- **transport**: the communication mechanism such as serial, TCP, USB, or vendor SDK call path
- **protocol**: the message/register/command semantics layered on a transport
- **device adapter**: the governed runtime object translating a concrete device/protocol implementation into platform concepts
- **capability model**: a declaration of what the adapter can read, write, configure, or report
- **logical signals/outputs**: the canonical platform objects surfaced from adapter capabilities

# 4. Device identity and lifecycle [SEC:UDQ-DEV-SPEC-001::4]

## 4.1 Stable identity [SEC:UDQ-DEV-SPEC-001::4.1]

Each integrated device shall have stable platform identity distinct from transient connection properties such as COM-port number or IP address.

## 4.2 Lifecycle states [SEC:UDQ-DEV-SPEC-001::4.2]

Adapters shall support explicit lifecycle states such as configured, initializing, connected, degraded, disconnected, faulted, disabled, and retiring/shutdown.

# 5. Adapter responsibilities [SEC:UDQ-DEV-SPEC-001::5]

A device adapter shall, at minimum:

- validate its configuration inputs
- manage connection/open/close lifecycle
- acquire or publish canonical signals with quality/timestamp information
- expose writable capabilities through the output/arbitration model rather than direct uncontrolled writes
- surface diagnostics and health information
- preserve enough evidence context for failures and meaningful state changes

# 6. Capability declaration [SEC:UDQ-DEV-SPEC-001::6]

## 6.1 Read capabilities [SEC:UDQ-DEV-SPEC-001::6.1]

Read capabilities shall declare what the adapter can surface as canonical signals, including type, units, quality semantics, update behavior, and origin metadata.

## 6.2 Write capabilities [SEC:UDQ-DEV-SPEC-001::6.2]

Write capabilities shall declare what the adapter can accept as platform-governed output requests, including supported value kinds, clamp/range expectations, acknowledgement/observation possibilities, and failure modes.

## 6.3 Service capabilities [SEC:UDQ-DEV-SPEC-001::6.3]

Where relevant, adapters may declare service capabilities such as device discovery, self-test, reset, or information-readback actions. These shall remain subject to authorization and evidence policy.

# 7. Protocol-specific specialization [SEC:UDQ-DEV-SPEC-001::7]

Protocol-specific specifications such as the Modbus specification may define deeper obligations for one adapter family. The device-abstraction layer shall generalize above them so that the rest of the platform works with canonical signals, outputs, health, and events rather than per-protocol special cases.

# 8. Configuration model [SEC:UDQ-DEV-SPEC-001::8]

Device-adapter configuration shall separate:

- identity
- connection properties
- protocol properties
- capability mapping
- polling/execution behavior
- retry/reconnect behavior
- evidence/logging policy where configurable

The UI should expose ordinary operator-friendly logical names while still providing engineering/service access to lower-level configuration detail where needed.

# 9. Signals and outputs integration [SEC:UDQ-DEV-SPEC-001::9]

Adapters shall publish data through the canonical signal model and accept writes through the canonical output/arbitration model. Adapter implementations shall not bypass platform ownership, interlock, or safe-state doctrine merely because a device SDK exposes a direct call.

# 10. Diagnostics and health integration [SEC:UDQ-DEV-SPEC-001::10]

Adapters shall surface enough information to support the diagnostics/watchdog/health model, including:

- connection state
- last-good communication time
- timeout/retry statistics where applicable
- protocol or decode anomalies
- degraded versus faulted distinction where meaningful

# 11. UI obligations [SEC:UDQ-DEV-SPEC-001::11]

The UI shall support, at minimum:

- device inventory/browse capability
- connection and health visibility
- capability inspection
- configuration review/edit workflows where authorized
- linkage from devices to signals, outputs, alarms, and diagnostics
- engineering/service detail without forcing ordinary operators to work in raw protocol terms for routine use

# 12. Validation and test obligations [SEC:UDQ-DEV-SPEC-001::12]

Device-adapter behavior shall be testable for:

- configuration validation
- startup/connect/disconnect/reconnect lifecycle
- canonical signal publication correctness
- output request handling through arbitration
- diagnostics/health publication
- graceful shutdown and restart behavior
- evidence generation for material faults and actions

# 13. Evidence obligations [SEC:UDQ-DEV-SPEC-001::13]

Material adapter lifecycle transitions, connection failures, recovery attempts, and service actions shall generate evidence consistent with the historian/event model.

# 14. Anti-patterns [SEC:UDQ-DEV-SPEC-001::14]

The platform shall avoid:

- device-specific logic leaking into core platform abstractions
- adapter writes that bypass output arbitration and safe-state handling
- connection identity coupled too tightly to unstable transport properties
- ordinary operator workflows requiring raw protocol/register fluency for routine monitoring and control
- health information trapped inside adapter logs without governed platform exposure



# 15. Support-pack and enhancement doctrine [SEC:UDQ-DEV-SPEC-001::15]

UniversalDAQ shall distinguish three support tiers:
- **generic** support where the platform makes an honest effort to detect, bind, and use a device without vendor enhancement,
- **protocol-family** support where a reusable protocol abstraction improves interpretation across a family of devices,
- **enhanced** support where an optional support pack or vendor bridge adds richer discovery, capability mapping, diagnostics, or workbench depth.

Support packs shall remain optional at the application-architecture level. Their absence shall not invalidate the universal core or generic/manual workflows.

## 15.1 No vendor leakage rule [SEC:UDQ-DEV-SPEC-001::15.1]
Vendor/device-specific terms such as channel naming, SDK flags, and model-specific setup semantics shall remain in edge metadata, support-pack code, or contextual workbenches. They shall not become required fields in the universal core model.

## 15.2 Compliance specimen rule [SEC:UDQ-DEV-SPEC-001::15.2]
A concrete device used to pressure-test the adapter model, such as the current LabJack U6 pilot, shall be treated as a compliance specimen and not as the hidden source of truth for the whole platform vocabulary.


# 16. Lifecycle and reconciliation companion specification [SEC:UDQ-DEV-SPEC-001::16]

The detailed device/point/signal/variable/logic lifecycle and reconciliation model is now captured in `UDQ-LIFECYCLE-SPEC-001`. That specification formalizes:
- stable versus transient identity,
- multiple-identical-device handling,
- point-to-signal binding,
- variable-layer introduction, and
- reconnect/remap outcomes.

## 16.1 First-party bridge doctrine [SEC:UDQ-DEV-SPEC-001::16.1]
Common hardware ecosystems may be supported through first-party auto-bridges that activate when standard dependencies are available. This is distinct from optional user plugins, which remain extra enhancement paths rather than the baseline support doctrine.

## 16.2 Multi-instance rule [SEC:UDQ-DEV-SPEC-001::16.2]
The adapter model shall support multiple simultaneous same-family devices without collapsing them into one inferred device identity. Distinguishing records by stable identity is mandatory wherever such identity is available.

# 11. Support tiers and bridge posture [SEC:UDQ-DEV-SPEC-001::11]
UniversalDAQ shall recognize three support tiers:
- **universal baseline**: honest generic effort without special device support,
- **first-party bridge**: official auto-enabled support when standard dependencies exist,
- **optional extension**: user/site/vendor-specific enhancements beyond the standard path.

A common device family such as LabJack shall be treated as a first-party bridge concern when officially supported, not as a mandatory custom plugin requirement.

# 12. Stable vs transient identity [SEC:UDQ-DEV-SPEC-001::12]
The platform shall treat serial number or other stable fingerprint as stronger identity than transient connection path. USB path, COM port, or session-local adapter ID shall be preserved as transient metadata and diagnostics context, not as the primary sameness key.

# 13. Same-family multi-instance handling [SEC:UDQ-DEV-SPEC-001::13]
The abstraction layer shall preserve distinct device records and connection instances for multiple same-family devices present at once. The platform shall not collapse two devices of the same model into one generic object merely because family and capability signature match.


# 9A. Canonical write-side handoff rule [SEC:UDQ-DEV-SPEC-001::9A]

Adapters that support writes shall accept canonical command intents and return canonical command outcomes. Core arbitration, replay, historian, and review layers shall not require transport-native command payloads, vendor error types, or hardware-brand branch logic to reason about a command outcome.

# 14A. Core contamination prohibition [SEC:UDQ-DEV-SPEC-001::14A]

The bounded mixed-source package shall be interpreted with the following prohibition in force:
- core/runtime/history/replay/review modules may consume canonical tags, canonical command objects, and generic runtime events only,
- adapter/vendor packages may not become required imports for those core modules,
- hardware-specific retry, framing, or transport semantics shall remain adapter-owned.

# 6.4 Channel metadata and provenance obligations [SEC:UDQ-DEV-SPEC-001::6.4]

For every readable point used in the operator-facing first-bench slice, the adapter seam shall preserve enough metadata to explain what the signal is and where it came from. At minimum the shell-facing summary should be able to recover:
- device identity key
- device display name and serial/transport where known
- adapter identifier
- point/channel identifier
- point class and engineering units where known
- stable provenance label suitable for diagnostics and review bundles
- adapter/vendor metadata that remains namespaced rather than leaking vendor terms into generic core semantics

The bounded first-signal implementation therefore treats point metadata and provenance as part of the governed adapter contract, not as ad hoc widget decoration.
