---
document_id: UDQ-GOV-GLO-001
title: Canonical Glossary and Ontology
revision: r0
status: WIP
document_class: glossary
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-SPEC-002
revision_history:
  - revision: r0
    date: 2026-03-21
    summary: Establishes canonical project vocabulary and high-level ontology anchors.
---
# Canonical Glossary and Ontology {#gov-glo-001.s01}

## 1. Purpose [SEC:UDQ-GOV-GLO-001::1]

This document defines the canonical meaning of core UniversalDAQ terms so that specifications, templates, package reports, and future code artifacts use the same vocabulary.

## 2. Core Ontology Rules [SEC:UDQ-GOV-GLO-001::2]

- A **device** is an addressable integration object with identity, capabilities, health, and one or more exposed points.
- A **signal** is a named data object with stable identity, type, quality state, timestamp, and value semantics.
- A **derived signal** is a signal computed from one or more other signals through governed logic.
- An **output** is a commandable target whose requested, applied, and observed states may differ.
- A **rule** is a governed condition-to-action definition that produces a request rather than an uncontrolled write.
- A **sequence** is a governed execution definition composed of steps and runtime state.
- An **event** is a discrete historical occurrence.
- An **alarm** is an event-bearing abnormal condition that may require acknowledgment or operator attention.
- A **profile** is a persisted user/session configuration bundle.
- A **workspace** is a major UI operating surface with a defined purpose.

## 3. Canonical Terms [SEC:UDQ-GOV-GLO-001::3]

### 3.1 Signal [SEC:UDQ-GOV-GLO-001::3.1]
A stable data object representing measured, imported, virtual, or derived information. Display names may change without changing signal identity.

### 3.2 Quality State [SEC:UDQ-GOV-GLO-001::3.2]
A classification that expresses whether a value is good, stale, invalid, disconnected, simulated, blocked, or otherwise degraded.

### 3.3 Output Request [SEC:UDQ-GOV-GLO-001::3.3]
A command intent issued by a user, rule, sequence, or remote surface for later arbitration and authorization.

### 3.4 Applied State [SEC:UDQ-GOV-GLO-001::3.4]
The backend-published state that the platform believes it has actually sent or committed after arbitration and capability checks.

### 3.5 Observed State [SEC:UDQ-GOV-GLO-001::3.5]
A measured, inferred, or device-reported state used to confirm actual behavior after an output request.

### 3.6 Interlock [SEC:UDQ-GOV-GLO-001::3.6]
A hard blocking condition that prevents a request from being applied while the blocking condition is active.

### 3.7 Permissive [SEC:UDQ-GOV-GLO-001::3.7]
A required enabling condition that must be true before an action may proceed.

### 3.8 Inhibit [SEC:UDQ-GOV-GLO-001::3.8]
A deliberate suppression or block applied by policy, state, or operator/service mode.

### 3.9 Safe State [SEC:UDQ-GOV-GLO-001::3.9]
The explicit state a subsystem or output must assume when risk, loss of health, or authority policy requires a controlled fallback.

### 3.10 Acknowledgment [SEC:UDQ-GOV-GLO-001::3.10]
A recorded user action indicating recognition of an alarm or event state without erasing historical truth.

### 3.11 Workspace [SEC:UDQ-GOV-GLO-001::3.11]
A major application surface such as Overview, Devices, Signals, Outputs, Rules, Sequences, Diagnostics, Historian/Review, or Remote.

### 3.12 Review Bundle [SEC:UDQ-GOV-GLO-001::3.12]
A governed export artifact set containing evidence, provenance, and context for later review.

## 4. Usage Rule [SEC:UDQ-GOV-GLO-001::4]

When a document uses one of the canonical terms above, the meaning in this glossary governs unless a stricter subordinate specification explicitly narrows the term for a documented subsystem context.
