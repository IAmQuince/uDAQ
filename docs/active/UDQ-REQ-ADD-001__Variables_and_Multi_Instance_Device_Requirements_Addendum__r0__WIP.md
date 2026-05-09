---
document_id: UDQ-REQ-ADD-001
title: Variables and Multi-Instance Device Requirements Addendum
revision: r0
status: WIP
document_class: requirement_addendum
owner: UniversalDAQ
depends_on:
  - "UDQ-LIFECYCLE-SPEC-001"
  - "UDQ-REQ-MAT-001"
  - "UDQ-DEV-SPEC-001"
revision_history:
  - "r0 | 2026-03-23 | Captured variable and multi-instance device requirement themes for the bounded lifecycle package line."
---
# UDQ-REQ-ADD-001
## Variables and Multi-Instance Device Requirements Addendum
### Revision
r0 — WIP

## Purpose

Capture the newly introduced requirement themes that must be folded into the next package:

- first-class variables
- multi-instance identical-device support
- dependency-aware signal and variable propagation
- safe reconnect/remap behavior when identical devices are present

---

## A. Variables

### A.1 First-class status
Variables shall be first-class runtime objects, not ad hoc UI-only calculations.

Variables may be derived from:
- one logical signal
- multiple logical signals
- constants
- other variables
- functions or expressions
- virtual/system values

### A.2 Variable uses
Variables shall be permitted as inputs to:
- logic blocks
- alarms
- historian/export
- visualizations
- command-generation logic
- user review and diagnostics

### A.3 Variable transparency
Each variable shall expose:
- variable name
- type and units
- formula or transform summary
- dependency list
- current value
- current quality/state
- invalid/degraded reason
- last successful compute time

### A.4 Variable failure handling
The system shall define explicit behavior when a variable loses one or more required dependencies.

Supported policies should include:
- invalidate immediately
- hold last value
- recompute with partial inputs if valid
- substitute defaults
- alarm on invalid
- inhibit dependent logic

### A.5 Variable traceability
The system shall preserve dependency traceability from:
- device point
- logical signal
- variable
- logic block
- output path

This traceability shall be visible in diagnostics and review artifacts.

---

## B. Multiple identical devices

### B.1 Support requirement
The system shall support two or more simultaneous devices of the same family/model.

Examples:
- two LabJack U6 devices
- two Arduino-class devices
- two identical remote I/O modules

### B.2 Identity requirement
The system shall distinguish identical devices by stable identity first, such as:
- serial number
- hardware fingerprint
- other stable identifiers

Port/path shall not be treated as the primary identity.

### B.3 Ambiguity requirement
If stable identity is unavailable or incomplete, the system shall:
- mark ambiguity explicitly
- avoid silent auto-binding for critical paths
- require review before restoring critical bindings

### B.4 Reconnect requirement
When one of multiple identical devices is disconnected and reattached:
- the system shall preserve prior stable-identity-based associations where possible
- the system shall not automatically swap bindings solely because physical port order changed
- the system shall present review flows when certainty is insufficient

### B.5 UX requirement
The UI shall differentiate multiple identical devices clearly using:
- stable identity where available
- user-assigned friendly labels
- role/context labels
- current connection metadata

Example:
- `LabJack U6 — Stack Bay A — serial 123456`
- `LabJack U6 — Stack Bay B — serial 789012`

---

## C. Immediate matrix-ready requirements

- The system shall support first-class variables derived from signals, constants, functions, and other variables.
- The system shall expose variable dependency and quality state in diagnostics and review surfaces.
- The system shall preserve traceability from raw source point through variable and logic dependencies to output paths.
- The system shall support multiple simultaneous devices of the same family/model.
- The system shall distinguish identical devices using stable identity before transient connection metadata.
- The system shall not automatically swap bindings between identical devices solely due to attachment order or port order changes.
- The system shall expose ambiguity explicitly when stable identity is insufficient for safe automatic restoration.

---

## D. Recommended document impacts

These requirements should be folded into the next package by updating:
- device lifecycle / reconciliation spec
- device onboarding UX flow spec
- UI state model
- requirements traceability matrix
- implementation transition plan
- gap report

