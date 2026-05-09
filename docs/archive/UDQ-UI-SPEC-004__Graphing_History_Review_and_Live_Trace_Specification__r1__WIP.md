---
document_id: UDQ-UI-SPEC-004
title: Graphing History Review and Live Trace Specification
revision: r1
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - "UDQ-HIS-SPEC-001"
  - "UDQ-EVT-SPEC-001"
  - "UDQ-UI-SPEC-001"
  - "UDQ-OUT-SPEC-001"
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-STD-002"
  - "UDQ-UI-MOD-001"
supersedes:
  - "UDQ-UI-SPEC-004__Graphing_History_Review_and_Live_Trace_Specification__r0__WIP.md"
revision_history:
  - "r1 | 2026-03-21 | Subsystem reconciliation pass: clarified live/historical/review/live-trace distinctions and requested/applied/observed overlays."
  - "revision: r0"
---
# Graphing History Review and Live Trace Specification {#ui-spec-004.s01}

## 1. Purpose [SEC:UDQ-UI-SPEC-004::1]

This document defines the behavior of the central graphing and review surface across live operation, historical review, and live trace/explainability use cases.

## 2. Graph Modes [SEC:UDQ-UI-SPEC-004::2]

The graph shall support:
- live window mode
- whole-session / historical review mode
- focused range exploration mode
- live trace / explainability overlay mode

## 2A. Semantic Closure and Anti-Conflation Rule [SEC:UDQ-UI-SPEC-004::2A]

This specification shall operationalize the glossary distinction between **live**, **historical**, **review mode**, and **live trace**. Graph mode indicators, overlays, and return-to-live behavior shall be explicit enough that a reviewer cannot confuse current runtime truth with evidence exploration. Requested/applied/observed overlays shall use the output-model meanings without collapsing them into a single line of truth.

## 3. Mode Distinction [SEC:UDQ-UI-SPEC-004::3]

Mode changes shall remain explicit. The UI shall make it obvious whether the user is viewing live data, historical review data, or an explainability overlay.

## 4. Trace Selection [SEC:UDQ-UI-SPEC-004::4]

The graph shall support named trace selection, visibility toggles, styling consistent with the visual language, and the ability to overlay related signals.

## 5. Event and Command Overlays [SEC:UDQ-UI-SPEC-004::5]

Where relevant, the graph shall support overlays for alarms, acknowledgments, commands, rule transitions, and sequence state changes.

## 6. Requested / Applied / Observed Views [SEC:UDQ-UI-SPEC-004::6]

For commandable behavior, the graph shall allow requested, applied, and observed state overlays where evidence relationships matter.

## 7. Return-to-Live Behavior [SEC:UDQ-UI-SPEC-004::7]

The graph shall provide an explicit and reliable return-to-live action from historical review or explored ranges.

## 8. Performance Rule [SEC:UDQ-UI-SPEC-004::8]

Historical scale and overlay richness shall not make the graph unusable for ordinary runtime monitoring.

## 9. Human Review Focus [SEC:UDQ-UI-SPEC-004::9]

A human pass should verify that a reviewer can tell what happened, when it happened, and whether the graph is live or historical without reading deep documentation.
