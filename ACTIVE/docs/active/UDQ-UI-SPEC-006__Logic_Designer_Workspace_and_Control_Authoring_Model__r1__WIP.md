---
document_id: UDQ-UI-SPEC-006
title: Logic Designer Workspace and Control Authoring Model
revision: r2
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
supersedes:
  - UDQ-UI-SPEC-006__Control_Workspace_and_Control_Authoring_Model__r0__WIP.md
revision_history:
  - revision: r2
    date: 2026-03-30
    summary: Documentation closeout. Added first executable draft/simulated slice expectations and bounded current node families.
  - revision: r1
    date: 2026-03-28
    summary: Initial Logic Designer workspace specification aligned to the post-shell UI model.
---

# Logic Designer Workspace and Control Authoring Model [SEC:UDQ-UI-SPEC-006::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-006::1]

This document defines the dedicated Logic Designer workspace as the primary UI environment for authoring, validating, simulating, monitoring, comparing, and auditing control behavior.

## 2. Governing User Promise [SEC:UDQ-UI-SPEC-006::2]

When a user enters Logic Designer, the UI should make them feel that they can:
- understand how behavior is constructed
- navigate from hardware source to logical signal to transform to sink without confusion
- simulate behavior before it is armed or applied
- monitor results in real time without leaving the application
- verify afterward why behavior occurred or did not occur

## 3. Canonical Authoring Chain [SEC:UDQ-UI-SPEC-006::3]

The Logic Designer shall organize authoring around the canonical chain:

**device point/source → logical signal → variable/transform layer → logic / state / sequence → command intent or sink binding → runtime evidence**

Sequences, protections, and modes are governed specializations on top of that chain.

## 4. Workspace Structure [SEC:UDQ-UI-SPEC-006::4]

The Logic Designer shall include, at minimum:
- a central design canvas and/or structured editor
- a palette/catalog of blocks and reusable modules
- an inspector dock for the selected object
- a lower watch/validation/simulation pane
- access to Device Explorer, Signal Explorer, and Logic Module Explorer inside the same shell

## 5. Design Surface Doctrine [SEC:UDQ-UI-SPEC-006::5]

The Logic Designer may expose both structured and visual representations, but the user shall be able to reason about the same underlying control assets through either representation.

### 5.1 Canvas expectations [SEC:UDQ-UI-SPEC-006::5.1]
The visual designer should support:
- source blocks
- math/transform/filter blocks
- timers, counters, latches, and stateful blocks
- decision/logic blocks
- controllers such as PID or bounded function blocks where supported later
- sink/output blocks
- groups, subflows/modules, and cross-canvas links to avoid spaghetti logic

### 5.2 Structured expectations [SEC:UDQ-UI-SPEC-006::5.2]
The structured representation should support:
- dependency inventories
- typed I/O summaries
- validation details
- searchable tables/cards for sources, transforms, logic, sequences, and sinks

## 6. Explorer Separation Rule [SEC:UDQ-UI-SPEC-006::6]

The user shall be able to browse:
- raw hardware sources and writable sinks in Device Explorer
- logical signals and derived variables in Signal Explorer
- reusable groups/subflows/modules in Logic Module Explorer

The designer shall not force these categories into one mixed tree.

## 7. Execution Postures [SEC:UDQ-UI-SPEC-006::7]

Logic Designer shall make these postures explicit:
- Draft
- Simulate
- Monitor Live
- Armed / Apply Ready
- Deployed / Observed

All simulated values shall remain visibly non-live. Monitoring live behavior shall remain distinct from editing draft structure.

## 8. Real-Time Monitoring in the Same Interface [SEC:UDQ-UI-SPEC-006::8]

The user shall be able to monitor live values, simulated values, or replayed values while remaining in the Logic Designer workspace. This is one of the main reasons Logic Designer remains inside the same application shell as Operate and Session Review.

## 9. Sequences and Convenience Actions [SEC:UDQ-UI-SPEC-006::9]

Sequence remains a required supporting feature because users often need convenient procedural control for timed waits, ramps, setpoint moves, digital state changes, and internal-variable manipulation without building a broader control module first.

## 10. Safe Write Reservations [SEC:UDQ-UI-SPEC-006::10]

The Logic Designer shall reserve explicit semantics for:
- read-only sources
- derived/watch-only outputs
- simulated sinks
- writable live sinks
- gated/blocked sinks
- authority/confirmation requirements before apply

## 11. Trust Mechanisms [SEC:UDQ-UI-SPEC-006::11]

The Logic Designer shall build trust through:
- explicit dependencies
- strong typing and units where relevant
- validation before apply
- simulation before deploy where appropriate
- draft-versus-deployed distinction
- requested-versus-observed evidence
- revision and audit history
- explainability surfaces for why-fired and why-blocked behavior

## 12. Human Review Focus [SEC:UDQ-UI-SPEC-006::12]

A reviewer should quickly confirm that Logic Designer:
- is a separate workspace from Operate but lives in the same shell
- supports navigation from raw device point to logical signal to sink without confusion
- supports simulation and live monitoring in the same interface
- treats grouping/subflow/module concepts as first-class anti-spaghetti tools
- reserves safe write posture rather than assuming every sink is freely writable

## 3A. User-Demo Logic Showcase [SEC:UDQ-UI-SPEC-006::3A]

The Logic Designer shall support a User-Demo posture in which pseudo-live sources, transforms, and sinks can be exercised without touching live hardware. A canonical early demo scenario shall include a pseudo Raspberry Pi-style input mapped through one or more functions to a pseudo LabJack-style DAC output while the operator monitors results in real time.

## 6A. Integrated Simulation and Monitoring [SEC:UDQ-UI-SPEC-006::6A]

The Logic Designer shall support distinct postures for:
- draft editing
- demo simulation
- live monitoring
- future armed application

These postures shall share a consistent shell but remain visually distinct. The designer shall never silently imply that simulated behavior is live hardware actuation.


## 2026-03-30 documentation closeout addendum — first executable slice
The current package line now documents a first executable **draft/simulated** Logic Designer slice. The bounded current node families are:
- Source
- Filter
- Math
- Comparator
- Sink

The implemented promise for this package is draft graph composition, watch/evaluation visibility, and simulated-only behavior. This package does **not** yet claim runtime-authoritative logic deployment, general live control execution, or broad sequencing depth from the Logic Designer surface.
