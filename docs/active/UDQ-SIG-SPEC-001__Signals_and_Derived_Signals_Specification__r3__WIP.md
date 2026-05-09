---
document_id: UDQ-SIG-SPEC-001
title: Signals and Derived Signals Specification
revision: r4
status: WIP
document_class: subsystem_spec
owner: UniversalDAQ
depends_on:
  - "UDQ-ARCH-NAR-001"
  - "UDQ-ARCH-NAR-002"
  - "UDQ-REQ-MAT-001"
  - "UDQ-QUAL-DEF-001"
  - "UDQ-UI-NAR-001"
  - "UDQ-UI-ARCH-001"
  - "UDQ-UI-MOD-001"
  - "UDQ-LOG-SPEC-001"
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-STD-002"
supersedes:
  - "UDQ-SIG-SPEC-001__Signals_and_Derived_Signals_Specification__r2__WIP.md"
revision_history:
  - "r4 | 2026-03-30 | Documentation closeout: added canonical device-I/O inventory expectations, single-owner tag/display-name semantics, and selected-device signal-lens rules."
  - "r3 | 2026-03-28 | Docs-only UI alignment pass: added plottable-signal registry expectations, SignalRef semantics, browse-lens aliases, and explicit separation between signal identity and trace presentation."
  - "r2 | 2026-03-21 | Subsystem reconciliation pass: clarified signal-vs-command semantics, quality-state ownership, and anti-conflation rules."
---
# Signals and Derived Signals Specification

This active revision is now read together with `UDQ-LIFECYCLE-SPEC-001`, `UDQ-PERF-SPEC-001`, and `UDQ-UI-SPEC-004` so signal identity, plottability, and graphing semantics remain aligned. [SEC:UDQ-SIG-SPEC-001::0]

## 1. Purpose [SEC:UDQ-SIG-SPEC-001::1]

This document defines the canonical signal model for UniversalDAQ. It establishes how raw measured values, imported values, device-backed states, virtual states, and derived values shall be represented, validated, published, historized, displayed, and consumed by other subsystems.

## 2. Additional design rule for the UI era [SEC:UDQ-SIG-SPEC-001::2]

UniversalDAQ shall treat any signal that is suitable for graphing, inspection, or monitoring as a **plottable signal** with stable identity. The same signal may be surfaced through multiple user-facing browse lenses without changing its identity.

## 3. SignalRef and browse-lens semantics [SEC:UDQ-SIG-SPEC-001::3]

### 3.1 SignalRef [SEC:UDQ-SIG-SPEC-001::3.1]
A SignalRef is the graph- and workspace-facing stable reference to a plottable signal.

### 3.2 Browse lenses [SEC:UDQ-SIG-SPEC-001::3.2]
The same signal may be surfaced through one or more browse lenses such as:
- Hardware
- Raw
- Logical
- Derived
- Control
- Favorites / Saved Sets

### 3.3 Identity rule [SEC:UDQ-SIG-SPEC-001::3.3]
Changing browse lens or display alias shall not create a new signal identity. Signal identity remains stable even if the same signal is displayed with different labels in different contexts.

## 4. Additional metadata classes [SEC:UDQ-SIG-SPEC-001::4]

Plottable signals shall support metadata sufficient for truthful UI presentation, including where applicable:
- stable signal ID
- source class (raw, logical, derived, control, simulated, historical)
- display aliases by lens
- units
- quality/freshness state
- provenance label
- plottable yes/no
- writable yes/no
- engineering range hints
- axis or grouping hints
- historian/report eligibility

## 5. Presentation separation rule [SEC:UDQ-SIG-SPEC-001::5]

Signal identity is not trace presentation. Color, line style, legend text, axis assignment, and alarm overlay treatment belong to the graphing/presentation layer, not to stable signal identity itself.

## 6. Human Review Focus [SEC:UDQ-SIG-SPEC-001::6]

A reviewer should quickly confirm that:
- signal identity survives naming-lens changes
- plottable signals carry enough metadata for truthful graphing
- the same signal can appear in different graph setups without changing identity
- signal identity and trace appearance remain distinct concerns

## 2026-03-28 implementation addendum — binding bridge
- The shell-facing Mapping Editor is the governed bridge between raw device endpoints and internal signal names.
- Device Explorer surfaces raw endpoint identity and capability. Signal Explorer surfaces internal signal identity and source lineage. The mapping surface is responsible for crossing between them explicitly.

## 2026-03-29 implementation addendum — generic baseline discovery continuity
- optional support packs enrich naming, protocol semantics, calibration, and richer read/write behavior, but they do not define whether baseline discovery is attempted at all.
- device-point to signal to variable flow remains backend-owned regardless of the shell's current draft or preview surfaces.


## 2026-03-30 documentation closeout addendum — canonical device-I/O inventory and tags
- A selected device may project a **canonical device-I/O inventory** containing device-scoped rows for real inputs, real outputs, internal associations, and virtual associations. That inventory is a device-centered inspection lens, not a redefinition of stable signal identity.
- Tag/display-name ownership shall be canonical. A tag edited against the canonical row or canonical signal identity flows outward to Signal Explorer, graph labels, Logic-source labels, and summaries. Other surfaces render that tag rather than redefining it.
- Signal Explorer remains a signal-first lens over stable signal identity. It may filter to the selected device context, but it shall not become a second tagging editor.
