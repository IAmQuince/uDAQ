---
document_id: UDQ-UI-SPEC-002
title: Widget Status and Visual Language Specification
revision: r1
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-UI-NAR-001
  - UDQ-UI-MOD-001
  - UDQ-EVT-SPEC-001
  - UDQ-DIAG-SPEC-001
  - UDQ-SEC-SPEC-001
  - UDQ-UI-SPEC-006
supersedes:
  - UDQ-UI-SPEC-002__Widget_Status_and_Visual_Language_Specification__r0__WIP.md
revision_history:
  - revision: r1
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Expanded the visual language to include draft/deployed, requested/observed, authority-source, and protection/trip semantics while keeping color from being the only cue.
  - revision: r0
    date: 2026-03-21
    summary: Defines the UI visual language for truth, health, authority, and editability.
---
# Widget Status and Visual Language Specification [SEC:UDQ-UI-SPEC-002::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-002::1]

This document defines the consistent visual treatment of truth state, health, authority, protection state, and editability across the UniversalDAQ UI.

## 2. Required Distinctions [SEC:UDQ-UI-SPEC-002::2]

The UI shall make these states visually distinct:
- live
- stale
- invalid
- disconnected
- simulated
- historical
- draft
- deployed
- draft differs from deployed
- blocked / interlocked / inhibited
- tripped / latched
- pending validation
- pending apply
- requested
- observed
- acknowledged
- manual authority
- sequence authority
- rule authority
- remote-origin authority

## 3. Visual Tokens [SEC:UDQ-UI-SPEC-002::3]

The visual language shall use a combination of:
- color
- text labels
- icons
- badges or pills
- row or card emphasis
- timeline or graph markers where appropriate

Color alone shall never carry all of the meaning for any safety, authority, or truth-critical distinction.

## 4. Value Presentation [SEC:UDQ-UI-SPEC-002::4]

Value widgets shall indicate both value and quality. Where a value is derived, stale, simulated, or historically retrieved, that context shall be inspectable without leaving the current surface.

## 5. Authority Presentation [SEC:UDQ-UI-SPEC-002::5]

Command-capable widgets shall expose:
- who or what currently owns authority
- whether the displayed state is requested or observed
- whether the point is blocked by a protection or higher-priority authority
- whether the action would currently require confirmation

## 6. Authoring Presentation [SEC:UDQ-UI-SPEC-002::6]

Authoring surfaces shall make explicit:
- clean draft
- dirty draft
- validation warning
- validation error
- simulation-ready
- apply-ready
- deployed
- superseded / rolled back

These states shall remain visible at inventory level and selected-object level.

## 7. Alarm, Event, and Protection Presentation [SEC:UDQ-UI-SPEC-002::7]

Alarmed states, returned-to-normal states, shelved states, suppressed states, acknowledged states, active protections, tripped states, and latched conditions shall each remain distinguishable.

## 8. Graph and Timeline Presentation [SEC:UDQ-UI-SPEC-002::8]

Graph markers and timeline markers shall preserve distinction between:
- value evidence
- command markers
- rule-firing markers
- sequence-transition markers
- alarm/event markers
- user annotations or notes

## 9. Consistency Rule [SEC:UDQ-UI-SPEC-002::9]

A state label shall mean the same thing everywhere it appears. The graph, tables, cards, inspector, and lower pane shall not silently reinterpret the same badge or icon differently.


## 8A. Current bounded first-bench slice additions [SEC:UDQ-UI-SPEC-002::8A]

The current bounded operator-flow slice shall surface, at minimum, the following truth-bearing visual labels in the same shell-facing path used for first signal and trusted session review:
- signal freshness (`fresh`, `stale`, `offline`, `simulated`, `pending`)
- signal provenance (device, adapter, point/channel, transport)
- control posture (`view_only`, `armed_control`, `engineering`)
- alarm posture (active alarm count, unacknowledged alarm count, highest active severity)
- action-audit posture (recent operator/session actions that materially changed what the operator saw)

These labels are intentionally text-first and evidence-aligned so that a future widget implementation cannot silently collapse them into color-only cues.

## 10. Human Review Focus [SEC:UDQ-UI-SPEC-002::10]

A reviewer should quickly confirm that the visual language now covers:
- truth quality
- authority source
- requested-versus-observed distinction
- draft/deployed distinction
- protection and trip visibility
