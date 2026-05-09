---
document_id: UDQ-UI-SPEC-003
title: Control Authoring Visual and Structured Roundtrip Specification
revision: r1
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-LOG-SPEC-001
  - UDQ-SIG-SPEC-001
  - UDQ-OUT-SPEC-001
  - UDQ-UI-SPEC-001
  - UDQ-UI-SPEC-006
supersedes:
  - UDQ-UI-SPEC-003__Rules_Editor_Visual_and_DSL_Roundtrip_Specification__r0__WIP.md
revision_history:
  - revision: r1
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Broadened the old rules-editor concept into a control-authoring roundtrip specification with structured-first views, optional diagrams, and secondary expression/DSL support.
  - revision: r0
    date: 2026-03-21
    summary: Defined the Rules workspace editor and visual/DSL roundtrip requirements.
---
# Control Authoring Visual and Structured Roundtrip Specification [SEC:UDQ-UI-SPEC-003::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-003::1]

This document defines the user-facing behavior of the Control workspace authoring surfaces, including structured authoring, optional diagram views, optional expression or DSL surfaces, validation, explainability, and roundtrip expectations.

## 2. Canonical Model Rule [SEC:UDQ-UI-SPEC-003::2]

All authoring views shall be alternate views onto one canonical control-asset model rather than separate authoring systems.

## 3. Primary Representation Rule [SEC:UDQ-UI-SPEC-003::3]

The primary authoring representation shall be structured:
- inventories
- tables
- cards
- inspectors
- guided editors

This is the default learnable path. Diagrammatic or DSL-like views may exist as secondary views for power users and advanced review.

## 4. Supported Authoring Views [SEC:UDQ-UI-SPEC-003::4]

The Control workspace may expose:
- inventory/table view
- card/detail view
- dependency/relationship diagram view
- optional expression or DSL view
- runtime explainability view
- audit/history comparison view

These are different views of the same objects, not competing object models.

## 5. Roundtrip Expectations [SEC:UDQ-UI-SPEC-003::5]

An asset saved from any supported authoring view shall render back into the other supported views without silent semantic drift. Information loss across supported views is not acceptable.

## 6. Validation Behavior [SEC:UDQ-UI-SPEC-003::6]

Validation shall expose syntax, dependency, type, units, authority, priority, and protection problems before apply. Validation failures shall not be hidden in logs alone.

## 7. Explainability Surface [SEC:UDQ-UI-SPEC-003::7]

The authoring environment shall expose:
- current truth
- blocked or indeterminate conditions
- affected actions or bindings
- last-change context
- upstream dependencies
- last-fired or last-attempted evidence when available

## 8. Sequence Convenience Surface [SEC:UDQ-UI-SPEC-003::8]

The Sequence subtab remains part of the roundtrip contract. It shall support deterministic procedural editing for timed steps, ramps, output changes, setpoint profiles, and internal or virtual variable changes. It is a convenience and power feature, not the only control-authoring metaphor.

## 9. Revision Visibility [SEC:UDQ-UI-SPEC-003::9]

The authoring environment shall preserve:
- draft versus deployed visibility
- change indicators
- comparison entry points
- audit/history references
- rollback and superseded-state visibility where available

## 10. Human Review Focus [SEC:UDQ-UI-SPEC-003::10]

A reviewer should quickly confirm that:
- structured authoring is primary
- diagrams and DSL-like surfaces are secondary
- roundtrip semantics remain deterministic
- sequence authoring remains preserved as a convenient supporting feature
