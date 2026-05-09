---
document_id: UDQ-UI-SPEC-002
title: Widget Status and Visual Language Specification
revision: r3
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
  - UDQ-UI-SPEC-002__Widget_Status_and_Visual_Language_Specification__r1__WIP.md
revision_history:
  - revision: r3
    date: 2026-03-28
    summary: Docs-only UI alignment pass. Added trace-presentation semantics, interactive legend expectations, and severity-based alarm overlays while preserving the rule that color shall never be the only cue.
  - revision: r1
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Expanded the visual language to include draft/deployed, requested/observed, authority-source, and protection/trip semantics while keeping color from being the only cue.
---
# Widget Status and Visual Language Specification [SEC:UDQ-UI-SPEC-002::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-002::1]

This document defines the consistent visual treatment of truth state, health, authority, protection state, editability, and trace presentation across the UniversalDAQ UI.

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
- warning alarm
- high alarm
- critical alarm

## 3. Visual Tokens [SEC:UDQ-UI-SPEC-002::3]

The visual language shall use a combination of:
- color
- text labels
- icons
- badges or pills
- row or card emphasis
- graph overlays and line ornamentation where appropriate
- selection highlighting and focus indication

Color alone shall never carry all of the meaning for any safety, authority, or truth-critical distinction.

## 4. Value and Trace Presentation [SEC:UDQ-UI-SPEC-002::4]

Value widgets and plotted traces shall indicate both value and quality. Where a value is derived, stale, simulated, disconnected, or historically retrieved, that context shall be inspectable without leaving the current surface.

The visual language shall support first-class trace-presentation properties such as:
- color
- line width
- solid/dashed/dotted line style
- point markers and point size
- opacity
- selected-trace highlight
- optional glow/halo treatment
- secondary-axis indication
- bounded blinking or pulse behavior when policy allows

## 5. Alarm and Severity Overlays [SEC:UDQ-UI-SPEC-002::5]

Alarm indication on traces shall be layered on top of the operator-selected base style rather than destructively replacing it.

Examples of allowed overlays include:
- warning halo or outline
- high alarm outline or edge emphasis
- critical alarm outline, pulse, or blink under stricter policy
- legend alarm badge and severity indicator

A user-selected trace style shall remain recognizable while active severity remains visually obvious.

## 6. Legend and Selection Presentation [SEC:UDQ-UI-SPEC-002::6]

The legend is an interactive control surface, not merely a passive label list. The legend shall support, where implemented:
- selected-trace emphasis
- current value and units
- visibility state
- axis assignment hint
- quality/freshness badge
- alarm badge
- quick style editing actions

## 7. Authority Presentation [SEC:UDQ-UI-SPEC-002::7]

Command-capable widgets shall expose:
- who or what currently owns authority
- whether the displayed state is requested or observed
- whether the point is blocked by a protection or higher-priority authority
- whether the action would currently require confirmation

## 8. Graph and Timeline Presentation [SEC:UDQ-UI-SPEC-002::8]

Graph markers and timeline markers shall preserve distinction between:
- value evidence
- command markers
- rule-firing markers
- sequence-transition markers
- alarm/event markers
- user annotations or notes

Historical and live plots shall also remain visually distinguishable.

## 9. Consistency Rule [SEC:UDQ-UI-SPEC-002::9]

A state label shall mean the same thing everywhere it appears. The graph, tables, cards, inspector, lower pane, and legend shall not silently reinterpret the same badge or icon differently.

## 10. Human Review Focus [SEC:UDQ-UI-SPEC-002::10]

A reviewer should quickly confirm that the visual language now covers:
- truth quality
- authority source
- requested-versus-observed distinction
- draft/deployed distinction
- protection and trip visibility
- trace-style flexibility
- alarm severity overlays that do not rely on color alone


## 2026-03-30 documentation closeout addendum — persistent bar semantics and honest affordances
- The persistent information bar shall reuse one stable semantic palette: green = healthy/ready/live, blue = informational or active mode, amber = degraded/limited/guarded, red = fault/disconnected/ESD, gray = inactive/none/hidden.
- The shell shall use `Applied`, `Draft`, `Unavailable`, and `Unmapped` as first-class visual-language states for bindings and mapping-related rows.
- Interactive controls shall be visually honest. A polished control must be either live and authoritative, live presentation-only, draft/preview, or explicitly not yet active.
