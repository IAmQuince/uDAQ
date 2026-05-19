---
document_id: UDQ-UI-INV-001
title: Genesys Feature Inventory and Preservation Map
revision: r3
status: WIP
document_class: ui_inventory
owner: UniversalDAQ
depends_on:
  - UDQ-UI-NAR-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-SPEC-004
  - UDQ-UI-SPEC-006
supersedes:
  - UDQ-UI-INV-001__Genesys_Feature_Inventory_and_Preservation_Map__r2__WIP.md
---

# Genesys Feature Inventory and Preservation Map [SEC:UDQ-UI-INV-001::0]

## Revision History [SEC:UDQ-UI-INV-001::0.1]
- r3: Docs-only UI refinement pass. Reframed this document as a feature-harvest and generalization map, corrected the title/header problem, and explicitly preserved sequence convenience without allowing Genesys page structure to drive UniversalDAQ architecture.
- r2: Earlier inventory and preservation pass.
- r1: Initial working issue.

## 1. Purpose [SEC:UDQ-UI-INV-001::1]

This document exists to harvest operator-value ideas from the earlier Genesys line and classify how, if at all, those ideas should be preserved in UniversalDAQ.

It is not an inheritance mandate and not an architecture source of truth.

## 2. What Was Valuable [SEC:UDQ-UI-INV-001::2]

The earlier Genesys line demonstrated value in:
- graph-first operation
- dockable engineering panels
- live sliding-window operation
- free graph exploration with return to live
- dense professional ergonomics
- convenient procedural sequencing
- direct visibility into outputs and setpoints in compact operator surfaces

## 3. What Must Be Generalized [SEC:UDQ-UI-INV-001::3]

The earlier line also carried device- and application-specific assumptions that UniversalDAQ shall not inherit as primitives. These include:
- page identities tied to one tool
- surfaces whose meaning depends on one hardware family
- assumptions that one style of sequence editing is the dominant control metaphor
- surfaces organized around one earlier application rather than around a universal workflow

## 4. Preservation Classes [SEC:UDQ-UI-INV-001::4]

### 4.1 Preserve almost directly [SEC:UDQ-UI-INV-001::4.1]
- graph-centered operating posture
- dockable/floating panel ergonomics
- obvious return-to-live behavior
- dense engineering-oriented shell behavior

### 4.2 Preserve but generalize [SEC:UDQ-UI-INV-001::4.2]
- convenient sequence editing for setpoints, outputs, and internal variables
- status/command compactness
- device-focused control pages, but only after converting them into universal Run/Control/System concepts
- output and command review linkage into broader evidence surfaces

### 4.3 Do not preserve as hard-coded assumptions [SEC:UDQ-UI-INV-001::4.3]
- exact page taxonomy
- device-specific naming
- one earlier tool’s mental model as the product identity
- hidden coupling between a single sequencer concept and all control authoring

## 5. Sequencer-Specific Preservation Guidance [SEC:UDQ-UI-INV-001::5]

One feature worth preserving is the convenience of a sequence or profile surface that can drive:
- external outputs
- internal variables
- timed value changes
- simple procedure steps

UniversalDAQ shall preserve that convenience inside the Sequence subtab of the Control workspace while avoiding the mistake of making sequence editing the only or dominant control-authoring metaphor.

## 6. Resulting Guidance for UniversalDAQ [SEC:UDQ-UI-INV-001::6]

UniversalDAQ should feel like an engineering cockpit, not like a clone. The correct design move is:
- preserve graph-centered ergonomics
- preserve docking
- preserve easy graph exploration and return to live
- preserve useful sequence convenience
- broaden the UI into a universal Run / Control / Review / System workspace architecture

## 7. Human Review Focus [SEC:UDQ-UI-INV-001::7]

A reviewer should quickly confirm that this document now functions as a feature-preservation map rather than as a hidden architecture source, and that the earlier title/header defect has been corrected.
