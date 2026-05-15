---
document_id: UDQ-LIFECYCLE-SPEC-001
title: Device, Point, Signal, Variable, Logic Lifecycle and Reconciliation Specification
revision: r0
status: WIP
document_class: lifecycle_spec
owner: UniversalDAQ
depends_on:
  - "UDQ-DEV-SPEC-001"
  - "UDQ-OUT-SPEC-001"
  - "UDQ-SIG-SPEC-001"
  - "UDQ-PROF-SPEC-001"
  - "UDQ-UI-DEVFLOW-001"
  - "UDQ-GOV-STD-001"
revision_history:
  - "r0 | 2026-03-23 | Introduced the vendor-agnostic lifecycle, binding, reconciliation, and restore doctrine for devices, points, signals, variables, logic, and outputs."
---
# UDQ-LIFECYCLE-SPEC-001
## Device, Point, Signal, Variable, Logic Lifecycle and Reconciliation Specification
### Revision
r0 — WIP

## 1. Purpose

Define the universal behavior for how UniversalDAQ shall handle:

- device discovery
- device identity and enrollment
- multiple simultaneous device instances, including multiple devices of the same family/model
- point/channel configuration
- logical signal binding
- variables derived from signals, constants, functions, or other variables
- logic consumption of signals and variables
- logical output binding
- safe behavior on signal loss
- disconnect, reconnect, remap, and recovery
- known-device restoration across sessions

This specification is vendor-agnostic in the core. The LabJack U6 is only a compliance specimen used to pressure-test the model.

---

## 2. Core doctrine

### 2.1 Universal rule
The core system shall never wire control logic directly to raw vendor channels, physical connection paths, or transient adapter instance IDs.

Logic must always consume **logical signals** and **variables**, not:
- USB ports
- transient adapter IDs
- vendor channel labels alone

The canonical chain is:

**physical device connection → device point → logical signal → variable/transform layer → logic block → command intent → logical output → governed output path**

### 2.2 Stable vs transient identity
The system must distinguish between:

#### Stable identity
What the device *is*:
- vendor/model family where known
- serial number where available
- stable hardware fingerprint where available

#### Transient connection identity
Where the device *is right now*:
- USB path
- COM port
- TCP endpoint
- session-local adapter instance

The system shall treat:
- serial number / stable fingerprint as primary identity
- port/path as transient connection metadata

### 2.3 Safe truth over false continuity
When a signal disappears, the system shall not silently assume:
- zero
- false
- off
- normal

unless that fallback behavior is explicitly configured.

Signal loss must be represented honestly and propagated through signal, variable, logic, and output dependency chains in a governed way. Performance shortcuts shall not erase or silently normalize that state.

### 2.4 Universal core, specialized edges
The core shall define:
- device lifecycle
- point lifecycle
- logical signal lifecycle
- variable lifecycle
- logic dependency behavior
- reconciliation behavior
- multiple-identical-device handling doctrine

Vendor-specific details shall live only in:
- first-party bridge layers
- optional workbenches
- extension metadata

### 2.5 Multi-instance device doctrine
The system shall support two or more simultaneous devices of the same family and model.

Examples include:
- two LabJack U6 devices
- two Arduino-class devices
- two identical Modbus I/O modules

The system shall not rely on model name alone to distinguish physical devices. It shall use stable identity first, and when stable identity is unavailable it shall expose ambiguity explicitly to the user.

---

## 3. Canonical entities

### 3.1 Device record
Represents a known physical or provisional device in the system.

#### Conceptual fields
- `device_record_id`
- `stable_identity`
- `device_family`
- `model_name`
- `serial_number`
- `fingerprint`
- `support_tier`
- `known_device_status`
- `last_seen_at`
- `saved_profile_links`
- `extension_metadata`

A device record survives across sessions. It is not the same thing as a live connection.

### 3.2 Connection instance
Represents one live or recent attachment of a device.

#### Fields
- `connection_instance_id`
- `device_record_id` if matched
- `detected_at`
- `transport_kind`
- `transport_path`
- `session_id`
- `adapter_id`
- `connection_state`
- `health_state`
- `identity_confidence`
- `capability_snapshot`

A device may have many connection instances over time.

### 3.3 Device point
Represents a configured, usable signal source or sink exposed by a device.

Examples:
- analog input
- digital input
- digital output
- analog output
- counter
- timer-derived value

#### Fields
- `point_id`
- `device_record_id`
- `point_class`
- `hardware_binding`
- `direction`
- `friendly_name`
- `units`
- `scaling`
- `quality_policy`
- `sampling_policy`
- `is_enabled`
- `extension_metadata`

### 3.4 Logical signal
Represents the universal contract between device points and the rest of the system.

Examples:
- `stack_voltage`
- `cell_temperature`
- `pump_enable_feedback`
- `cathode_pressure`

#### Fields
- `logical_signal_id`
- `signal_name`
- `expected_type`
- `engineering_units`
- `binding_policy`
- `missing_signal_policy`
- `quality_requirements`
- `bound_source_point_ids`
- `current_binding_state`
- `last_value`
- `last_good_value`
- `current_quality`
- `dependency_tags`

Logic shall use these, not raw points.

### 3.5 Variable
Represents a reusable value in the system that may be derived from:
- a logical signal
- a constant
- another variable
- a function of multiple signals/variables
- a virtual/system source

Variables are first-class citizens and may feed:
- logic blocks
- alarms
- derived displays
- historian/export traces
- command logic
- user expressions and computed views

#### Variable classes
- `constant`
- `alias`
- `expression`
- `filtered`
- `latched`
- `stateful`
- `virtual_system`
- `manual_entry` where governed

#### Fields
- `variable_id`
- `variable_name`
- `variable_class`
- `expected_type`
- `engineering_units`
- `expression_definition` or equivalent transform definition
- `input_dependency_ids`
- `current_value`
- `last_good_value`
- `current_quality`
- `evaluation_state`
- `missing_input_policy`
- `recompute_policy`
- `persistence_policy`
- `extension_metadata`

### 3.6 Logic block
Represents a computation, rule, interlock, permissive, state machine, or transformation that consumes logical signals and variables and produces derived signals, variables, alarms, or command intents.

#### Fields
- `logic_block_id`
- `logic_kind`
- `input_signal_ids`
- `input_variable_ids`
- `output_signal_ids`
- `output_variable_ids`
- `missing_input_behavior`
- `quality_requirements`
- `evaluation_state`
- `inhibit_state`
- `last_evaluated_at`

### 3.7 Command intent
Represents a requested output-related action before transport/application.

#### Fields
- `command_intent_id`
- `source_logic_block_id` or user source
- `target_logical_output_id`
- `requested_value`
- `authorization_state`
- `arbitration_state`
- `dependency_state`
- `handoff_state`

### 3.8 Logical output
Represents an abstract controllable output path.

Examples:
- `pump_enable_cmd`
- `heater_setpoint_cmd`
- `stack_fan_enable_cmd`

#### Fields
- `logical_output_id`
- `friendly_name`
- `expected_type`
- `binding_policy`
- `bound_target_point_id`
- `safety_policy`
- `fallback_policy`
- `last_command_intent_id`

---

## 4. Support tiers

### Tier 1 — Universal baseline
The app makes an honest generic effort:
- detect candidate device endpoints
- allow manual configuration where possible
- surface provisional identity
- expose generic diagnostics
- permit generic point definitions if transport allows

### Tier 2 — First-party bridge
Official bridge present and dependency available:
- richer identity
- proper capability discovery
- correct read/write support
- better metadata
- first-party diagnostics

### Tier 3 — Optional extension/workbench
Additional value on top:
- specialized setup helpers
- templates
- instrument-specific panels
- advanced diagnostics
- custom site logic or decoders

---

## 5. Lifecycle state models

### 5.1 Device lifecycle states
- `candidate`
- `identified`
- `enrolled`
- `configured`
- `active`
- `degraded`
- `disconnected`
- `reattached`
- `replaced`

### 5.2 Point lifecycle states
- `discovered`
- `defined`
- `bound`
- `live`
- `stale`
- `lost`
- `substituted`
- `rebound`

### 5.3 Logical signal lifecycle states
- `unresolved`
- `healthy`
- `degraded`
- `stale`
- `invalid`
- `substituted`
- `inhibited`
- `rebound`

### 5.4 Variable lifecycle states
- `defined`
- `resolvable`
- `healthy`
- `degraded`
- `stale`
- `invalid`
- `substituted`
- `latched`
- `inhibited`

### 5.5 Logic block lifecycle states
- `ready`
- `degraded`
- `inhibited`
- `faulted`
- `safe_hold`

### 5.6 Logical output lifecycle states
- `unbound`
- `ready`
- `blocked`
- `handoff_pending`
- `applied_unverified`
- `verified`
- `degraded`
- `lost`

---

## 6. Identity and matching model

### 6.1 Identity precedence
When matching an attached device to an existing device record, the system shall use:

#### First priority
- serial number
- stable hardware fingerprint

#### Second priority
- model family
- vendor identity
- capability signature

#### Third priority
- prior user association
- previous known transport characteristics

#### Lowest priority
- port/path

### 6.2 Match confidence classes
- `exact_match`
- `probable_match`
- `possible_match`
- `no_match`

### 6.3 Port migration handling
If the same physical device is unplugged from one port and plugged into another:
- old connection instance becomes `disconnected`
- new connection instance is created
- stable identity governs matching
- the device record remains the same
- prior point bindings remain attached to the device record
- logical signals and variables are restored through reattachment if configured policy allows
- port metadata is updated, not treated as a different device unless evidence says otherwise

### 6.4 Multiple simultaneous identical devices
If two or more devices of the same family/model are present simultaneously, the system shall:
- create distinct device records when stable identity distinguishes them
- maintain distinct connection instances even if model/family are identical
- expose separate device cards, point inventories, and binding options
- prevent accidental cross-binding by requiring stable identity match or explicit user confirmation

If stable identity is unavailable or incomplete, the system shall:
- mark the devices as ambiguous
- avoid silent auto-binding to critical logic
- present user review and naming/association tools

---

## 7. Onboarding workflow

### 7.1 Discovery stage
The app detects a device candidate and creates a connection instance.

User sees:
- device family/model where known
- serial where known
- support tier
- current state: discovered, not yet configured

Actions:
- Quick Start
- Configure Device
- Ignore for now
- Diagnostics

### 7.2 Enrollment stage
The system determines whether the device is:
- new
- previously known
- likely replacement
- ambiguous
- one of multiple similar devices

If known:
- restore offer may appear

If new:
- create device record

### 7.3 Configuration stage
The user chooses which device points to activate and how to define them.

For each selected point:
- friendly name
- point role
- units/scaling
- input/output direction
- quality policy
- sampling policy
- whether the point should bind to an existing logical signal or create a new one

### 7.4 Binding stage
Configured points are mapped to logical signals or logical outputs.

Example:
- `DevicePoint(U6 serial 123456 / AIN0)` binds to `LogicalSignal(stack_voltage)`

Example output:
- `LogicalOutput(pump_enable_cmd)` binds to `DevicePoint(U6 serial 123456 / FIO3 output)`

### 7.5 Variable stage
The user may define variables based on:
- one signal
- multiple signals
- constants
- expressions
- filters
- stateful transforms
- virtual system values

Examples:
- `stack_power = stack_voltage * stack_current`
- `pressure_delta = anode_pressure - cathode_pressure`
- `pump_demand = max(flow_request, recirculation_request)`
- `is_warm = cell_temp > 45 C`

Variables shall be bindable into logic exactly like signals, while preserving dependency traceability.

### 7.6 Activation stage
Once relevant bindings exist:
- live acquisition begins
- variables compute according to recompute policy
- logic sees signal and variable values plus quality
- outputs remain governed by authorization, interlock, and dependency state
- historian and diagnostics become fully informative

---

## 8. Signal and variable binding doctrine

### 8.1 Binding levels
Bindings must be explicit at four levels:

#### Device point binding
Physical source/sink to point definition.

#### Logical signal binding
Point to universal signal.

#### Variable dependency binding
Signals/variables/constants/functions to variable definition.

#### Logical output binding
Universal output to physical target point.

### 8.2 Binding policies
- `strict_identity`
- `same_device_same_point`
- `same_capability_same_type`
- `manual_review_required`
- `auto_rebind_if_confident`

### 8.3 Variable dependency policies
Variables shall support dependency policies such as:
- `all_inputs_required`
- `minimum_input_count`
- `degrade_if_partial`
- `substitute_if_missing`
- `hold_last_computed`
- `invalidate_immediately`

### 8.4 Variable transparency doctrine
Every variable shall be inspectable in terms of:
- current formula or transform definition
- dependency list
- current value
- current quality
- last successful compute time
- why it is degraded/invalid if applicable

Variables must not become opaque hidden magic in the system.

---

## 9. Missing signal and variable behavior

### 9.1 Signal loss is first-class
When a source point disappears, the system shall explicitly represent:
- stale
- disconnected
- bad quality
- substituted
- unknown

### 9.2 Per-signal missing-signal policies
Each logical signal should support:
- `immediate_invalid`
- `hold_then_stale`
- `substitute_fixed_value`
- `substitute_backup_signal`
- `safe_inhibit_dependents`
- `alarm_on_loss`
- `log_only`

### 9.3 Per-variable missing-input policies
Each variable shall support configurable behavior when dependencies are missing or degraded:
- `invalidate`
- `hold_last_value`
- `recompute_with_available_inputs`
- `substitute_defaults`
- `alarm_on_invalid`
- `defer_update`

### 9.4 Downstream behavior
Logic blocks must declare how they respond to degraded or missing signal/variable inputs. Examples:
- inhibit output-generating logic
- hold last safe output intent
- force safe state
- continue with warning for noncritical display logic
- switch to backup path

---

## 10. Disconnect, reconnect, and remap behavior

### 10.1 Disconnect event
When a live connection disappears:
- connection instance becomes `disconnected`
- affected points become `lost` or `stale`
- affected logical signals transition accordingly
- affected variables reevaluate and may degrade or invalidate
- dependent logic blocks reevaluate and may inhibit
- governed outputs may be blocked or forced safe depending on safety policy
- historian evidence is created
- diagnostics update immediately

### 10.2 Reconnect same device, same session
If the same stable device identity returns:
- create a new connection instance
- mark device record as `reattached`
- compare prior point configurations to current capability inventory
- if confident, restore point and signal bindings automatically per policy
- reevaluate dependent variables
- mark recovered paths `rebound`
- keep output-driving behavior governed; do not silently resume unsafe active control modes

### 10.3 Reconnect same device, different port
Same as above, but additionally:
- update transient connection metadata
- log port migration in evidence and diagnostics
- do not treat this as a different device when stable identity matches

### 10.4 Reconnect in a new session
If the same device is known from a prior session, the system may offer safe restore for:
- point definitions
- logical bindings
- variable definitions
- display/workspace state
- diagnostics preferences

The system shall not silently resume:
- active governed outputs
- armed control modes
- unsafe machine-affecting states

### 10.5 Replacement device
If a different physical device appears where a prior one was expected:
- do not silently assume interchangeability
- compare capability, type, and role compatibility
- generate remap suggestions only
- require confirmation unless policy explicitly allows auto-acceptance

### 10.6 Two identical devices during reconnect/replacement
If two identical devices are present and one disappears/reappears:
- the system shall preserve stable-identity-based associations where possible
- the system shall not automatically swap bindings between same-model devices solely due to attachment order or port order
- if confidence is not exact, the system shall require user review before restoring critical bindings

---

## 11. Reconciliation engine

### 11.1 Responsibilities
The reconciliation layer shall:
- compare old and new connection instances
- match new connections to existing device records
- compare point inventories
- evaluate candidate source replacements
- evaluate variable dependency impact
- propose remaps
- apply auto-rebind when policy allows
- emit evidence and diagnostics for each decision

### 11.2 Reconciliation outcomes
- `restored_exact`
- `restored_with_port_change`
- `restored_partial`
- `candidate_remap_requires_review`
- `new_device_unbound`
- `replacement_detected`
- `ambiguous_same_model_devices`

### 11.3 Auto-remap policy
Auto-remap shall happen only when:
- stable identity matches strongly
- point identity or equivalent capability mapping matches
- data type and role are compatible
- variable dependencies remain valid or can be safely revalidated
- configured policy permits automatic restoration

Otherwise the system shall present a remap review workflow.

---

## 12. UI and UX behavior

### 12.1 Core user experience stages
The system should make these stages explicit:
- Discover
- Configure
- Bind
- Derive
- Run
- Degrade / Recover

### 12.2 User-visible objects
#### Device card
Should show:
- identity
- connection state
- support tier
- health
- known-device status
- ambiguity state if multiple similar devices exist
- current session status

#### Point list
Should show:
- friendly name
- hardware binding
- direction
- value
- quality
- freshness
- logical binding

#### Signal list
Should show:
- logical signal name
- source point
- current value
- quality/state
- missing-signal policy
- dependent variable count
- dependent logic count

#### Variable list
Should show:
- variable name
- definition or formula summary
- dependencies
- current value
- quality/state
- invalid/degraded reason
- dependent logic count

#### Dependency view
Should show:
- which signals feed which variables
- which variables feed which logic blocks
- which outputs are affected by missing/degraded paths

#### Reconciliation panel
Should show:
- lost bindings
- candidate replacements
- confidence and reason
- accept / reject / manual remap actions

### 12.3 On disconnect
The app should clearly show:
- which device disconnected
- how many points are affected
- how many signals are degraded
- how many variables are invalid/degraded
- how many control paths are inhibited
- how many output paths are blocked

### 12.4 On known-device reconnect
The app should clearly show:
- known device reattached
- previous bindings restored
or
- N bindings need review

### 12.5 On two identical devices
The app should clearly differentiate them by:
- stable identity where available
- friendly user labels
- current connection metadata
- role association in the project

Example:
- `LabJack U6 — Stack Bay A — serial 123456`
- `LabJack U6 — Stack Bay B — serial 789012`

---

## 13. Safety and governance

### 13.1 Output behavior under signal/variable loss
The system must define output-path policies for dependency loss. Examples:
- block new commands
- hold last safe command intent
- force safe fallback
- inhibit logic-generated outputs until source health is restored

This should be configured per logical output or logic domain.

### 13.2 Authorization remains separate
Reconnect, remap, and restore do not bypass authorization.

The system may restore:
- bindings
- variables
- visual/workspace state
- diagnostics posture

But governed output actions must still pass through:
- authorization
- interlock / permissive
- arbitration
- adapter handoff

### 13.3 Evidence requirements
All significant lifecycle events should produce attributable evidence:
- discovery
- enrollment
- configuration changes
- signal binding changes
- variable definition changes
- disconnect
- reconnect
- remap acceptance/rejection
- safe inhibits due to signal/variable loss
- ambiguity resolution for identical devices

---

## 14. Persistence model

### 14.1 Persist what is stable
Profiles and saved workspaces should persist:
- known device identity
- point definitions
- logical signal bindings
- variable definitions
- logical output bindings
- missing-signal policies
- missing-variable-input policies
- display/workspace preferences
- diagnostics preferences
- extension metadata in namespaced sections

### 14.2 Do not persist transient transport as identity
Port/path may be stored for diagnostics and convenience, but must not be treated as the primary device key.

### 14.3 Extension data
Vendor-specific settings must live in bounded extension sections, not pollute the universal schema.

Example concept:
- `extensions.labjack.{...}`

---

## 15. Universal vs vendor-specific boundary

### 15.1 Core may know
- device
- point
- signal
- variable
- logic
- output
- quality
- freshness
- binding
- identity confidence
- support tier
- workbench availability

### 15.2 Core must not know
- `U6`
- `AIN0`
- `FIO3`
- LabJack driver method names
- vendor-only channel addressing rules

### 15.3 Vendor bridge may know
- exact channel naming
- exact transport semantics
- vendor identity rules
- vendor-specific diagnostics
- workbench helpers

---

## 16. Derived requirement set

### 16.1 Identity and lifecycle
- The system shall distinguish stable device identity from transient connection metadata.
- The system shall preserve device identity across disconnect and reconnect when stable identity matches.
- The system shall treat port/path changes as transient unless evidence indicates device replacement.
- The system shall support multiple simultaneous devices of the same family/model without conflating their identities.

### 16.2 Configuration and binding
- The system shall allow device points to be defined independently from logical signal bindings.
- The system shall allow logical signals to be consumed by logic independently from raw device channel naming.
- The system shall support first-class variables derived from signals, constants, functions, and other variables.
- The system shall allow logical outputs to bind to physical targets independently from control logic.

### 16.3 Missing signal and variable handling
- The system shall explicitly represent stale, lost, invalid, substituted, and rebound signal states.
- The system shall explicitly represent degraded, invalid, substituted, and latched variable states.
- The system shall support per-signal missing-data policies.
- The system shall support per-variable missing-input policies.
- The system shall prevent unsafe control behavior when critical input signals or variables are unavailable, according to configured policy.

### 16.4 Reconciliation
- The system shall evaluate reconnect events against existing device records using stable identity first.
- The system shall support automatic rebinding only when configured policy and confidence permit it.
- The system shall provide a review path for uncertain remap candidates.
- The system shall not automatically swap bindings between two identical devices solely because attachment order or port order changed.

### 16.5 UI and UX
- The system shall expose discovery, configuration, binding, derive, active, degraded, and recovery states clearly to the user.
- The system shall surface affected point, signal, variable, and logic counts on disconnect.
- The system shall offer safe restore for known devices across sessions.
- The system shall distinguish identical devices clearly in the user experience.

### 16.6 Governance
- The system shall preserve evidence for discovery, disconnect, reconnect, remap, ambiguity resolution, variable-definition change, and inhibit events.
- The system shall not automatically resume governed machine-affecting output behavior solely because a known device reconnects.

---

## 17. Implementation implications

The next implementation work should include at minimum:
- `DeviceRegistryService`
- `PointConfigurationService`
- `SignalBindingService`
- `VariableDefinitionService`
- `ReconciliationService`
- `LogicDependencyService`

Session model additions should include:
- device lifecycle inventory
- point inventory
- logical signal health summary
- variable health summary
- unresolved binding inventory
- remap candidate inventory
- recovery state summary

Diagnostics should be able to dump:
- known devices
- live connections
- point-to-signal bindings
- variable definitions and health
- signal and variable dependency impact
- remap candidates
- reconciliation outcomes

---

## 18. Lock now vs later

### Lock now
- stable vs transient identity doctrine
- logical signals as the interface to logic
- variables as first-class derived inputs
- point/signal/variable/output separation
- missing-signal and missing-variable state model
- reconnect/remap policy framework
- safe restore doctrine
- disconnect/reconnect UX semantics
- multi-identical-device doctrine

### Keep flexible for later
- exact visual layouts
- exact workbench page arrangement
- cosmetic presentation
- advanced vendor-specific tools
- final detailed logic authoring UI

---

## 19. Bottom line

The formal universal model is:

**Devices are enrolled by stable identity. Points are configured from device capabilities. Points bind into logical signals and logical outputs. Variables may be derived from signals, constants, functions, and other variables. Logic consumes logical signals and variables, not raw hardware channels. Signal and variable loss are explicit and governed. Reconnection is reconciled by identity, not port. Restoration is safe, attributable, and policy-driven. Multiple identical devices are supported without conflating their identities.**
