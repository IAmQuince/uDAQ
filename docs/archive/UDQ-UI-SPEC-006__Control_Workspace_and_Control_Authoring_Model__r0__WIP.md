---
document_id: UDQ-UI-SPEC-006
title: Control Workspace and Control Authoring Model
revision: r0
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-MOD-001
  - UDQ-SIG-SPEC-001
  - UDQ-LOG-SPEC-001
  - UDQ-SEQ-SPEC-001
  - UDQ-OUT-SPEC-001
  - UDQ-LIFECYCLE-SPEC-001
---

# Control Workspace and Control Authoring Model [SEC:UDQ-UI-SPEC-006::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-006::1]

This document defines the Control workspace as the primary UI environment for authoring, validating, simulating, comparing, and auditing control behavior.

Its purpose is to make the control system feel dependable, inspectable, and teachable rather than magical or fragile.

## 2. Governing User Promise [SEC:UDQ-UI-SPEC-006::2]

When a user enters the Control workspace, the UI should make them feel that they can:
- understand how behavior is constructed
- tell what the system will do before it is deployed
- verify afterward why it did what it did
- compare drafts and deployed behavior without confusion

## 3. Core Authoring Chain [SEC:UDQ-UI-SPEC-006::3]

The Control workspace shall organize authoring around the canonical chain:

**signals → variables → conditions and decisions → actions → runtime evidence**

Sequences, protections, and modes are governed specializations on top of that chain.

## 4. Control Workspace Subtabs [SEC:UDQ-UI-SPEC-006::4]

The Control workspace shall provide the following subtabs or equivalent sub-surfaces:

1. Overview  
2. Variables  
3. Logic  
4. Sequence  
5. Interlocks / Protections  
6. Actions / Bindings  
7. Modes / States  
8. Test / Simulation  
9. Audit / History

## 5. Overview Subtab [SEC:UDQ-UI-SPEC-006::5]

Overview is the landing surface for Control. It shall summarize:
- count and status of authored assets
- validation warnings and errors
- last simulation or replay result
- draft-versus-deployed difference summary
- recent changes
- deployment readiness posture

Overview is a trust surface first, not a deep editor first.

## 6. Variables Subtab [SEC:UDQ-UI-SPEC-006::6]

Variables shall include:
- raw device-backed values
- scaled values
- filtered values
- derived/calculated values
- constants and setpoints
- timers, counters, and latches
- operator-entered parameters
- mode/status flags
- internal or virtual variables

Each variable shall show:
- name
- type and units where relevant
- source
- dependency chain
- where it is used
- runtime quality and last value
- validation issues

## 7. Logic Subtab [SEC:UDQ-UI-SPEC-006::7]

Logic is the primary decision-authoring surface.

### 7.1 Primary representation [SEC:UDQ-UI-SPEC-006::7.1]
The default representation shall be structured rules shown as rows, cards, or equivalent guided editors rather than an unbounded free-form canvas.

### 7.2 Minimum rule fields [SEC:UDQ-UI-SPEC-006::7.2]
Each rule shall be able to expose:
- name
- enabled state
- scope or applicable modes
- inputs used
- condition
- persistence or debounce requirement
- action(s)
- priority
- latch or reset behavior
- inhibit conditions
- last evaluation
- last fired or last blocked reason

### 7.3 Alternate views [SEC:UDQ-UI-SPEC-006::7.3]
The Logic subtab may provide alternate views such as dependency diagrams, relationship maps, or optional expression/DSL views, but these remain secondary to structured-first authoring.

## 8. Sequence Subtab [SEC:UDQ-UI-SPEC-006::8]

Sequence remains a required feature because users often need convenient procedural control.

### 8.1 Purpose [SEC:UDQ-UI-SPEC-006::8.1]
The Sequence subtab is for ordered steps and deterministic transitions, including convenient profiles for:
- setpoint changes
- analog or DAC output changes
- digital state changes
- external command steps
- internal or virtual variable changes
- timed waits, ramps, and holds

### 8.2 Minimum sequence fields [SEC:UDQ-UI-SPEC-006::8.2]
A sequence shall expose:
- ordered steps
- step actions
- hold/wait conditions
- timeouts
- retries
- abort behavior
- pause/resume
- completion criteria
- manual jump permissions
- current or last runtime step evidence where available

### 8.3 Sequence boundary [SEC:UDQ-UI-SPEC-006::8.3]
Sequence is a convenient supporting control surface. It is not the only or mandatory control metaphor for the whole product.

## 9. Interlocks / Protections Subtab [SEC:UDQ-UI-SPEC-006::9]

Protections shall remain distinct from ordinary logic. This subtab shall define:
- permissives
- inhibits
- warnings
- soft limits
- hard limits
- trips
- latch and reset behavior
- required safe-state consequences

Users shall be able to tell what condition triggers a protection, what it blocks or forces, and how it clears.

## 10. Actions / Bindings Subtab [SEC:UDQ-UI-SPEC-006::10]

Actions define what the control system can actually do. Supported action classes may include:
- set internal value
- request external output or device command
- change target/setpoint
- start or stop a sequence
- raise event or alarm
- write note or annotation
- enable or disable another asset

For actuation-oriented actions, the UI shall expose requested-versus-observed effect where available.

## 11. Modes / States Subtab [SEC:UDQ-UI-SPEC-006::11]

Modes / States provide higher-level orchestration. They define:
- named contexts
- allowed logic or sequence activity
- allowed transitions
- entry and exit conditions
- mandatory protections or restrictions

This subtab exists so that higher-level orchestration does not have to be hidden inside raw rule rows.

## 12. Test / Simulation Subtab [SEC:UDQ-UI-SPEC-006::12]

Test / Simulation is a first-class trust surface.

It shall support, where available:
- replay of recorded data
- injection of test values
- missing/stale/bad-data simulation
- action failure simulation
- rule firing review
- sequence progression review
- blocked-action review
- expected-versus-observed simulation outcomes

All outputs from this subtab shall remain clearly non-live.

## 13. Audit / History Subtab [SEC:UDQ-UI-SPEC-006::13]

Audit / History shall support:
- revision comparison
- who/what changed
- validation history
- simulation history
- deploy history
- comments and notes
- rollback context

## 14. Trust Mechanisms [SEC:UDQ-UI-SPEC-006::14]

The Control workspace shall build trust through:
- explicit dependencies
- strong typing and units where relevant
- validation before apply
- simulation before deploy where appropriate
- draft-versus-deployed distinction
- requested-versus-observed evidence
- revision and audit history
- explainability surfaces for why-fired and why-blocked behavior

## 15. Progressive Learnability Rule [SEC:UDQ-UI-SPEC-006::15]

The Control workspace shall be deep without feeling crowded. It shall allow:
- a simple guided path for first use
- more advanced views when needed
- power features without making the default experience feel like programming for its own sake

## 16. Contextual Toolbar [SEC:UDQ-UI-SPEC-006::16]

The Control workspace should expose a contextual toolbar with actions such as:
- New
- Clone
- Validate
- Simulate
- Compare Draft vs Deployed
- Apply / Deploy
- Roll Back
- Search / Filter
- Show Dependencies
- Export Report
- Generate Diagnostics

These belong in the workspace context rather than overloading the global shell toolbar.

## 17. Human Review Focus [SEC:UDQ-UI-SPEC-006::17]

A reviewer should quickly confirm that the Control workspace:
- is broader than a rules editor
- preserves sequence convenience as a supporting feature
- separates protections from ordinary logic
- includes test/simulation and audit as first-class trust surfaces
- gives the user a structured, inspectable path to build behavior they can trust
