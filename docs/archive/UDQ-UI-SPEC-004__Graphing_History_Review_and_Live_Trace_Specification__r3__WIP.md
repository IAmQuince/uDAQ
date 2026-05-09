---
document_id: UDQ-UI-SPEC-004
title: Graphing History Review and Live Trace Specification
revision: r3
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-HIS-SPEC-001
  - UDQ-EVT-SPEC-001
  - UDQ-UI-SPEC-001
  - UDQ-OUT-SPEC-001
  - UDQ-GOV-GLO-001
  - UDQ-GOV-STD-002
  - UDQ-UI-MOD-001
supersedes:
  - UDQ-UI-SPEC-004__Graphing_History_Review_and_Live_Trace_Specification__r2__WIP.md
revision_history:
  - revision: r3
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Added explicit live-follow/sliding-window/whole-history/explore semantics, truthful decimation expectations, user-selected time horizon, evidence linking, and richer overlay rules.
  - revision: r2
    date: 2026-03-22
    summary: Added bounded implementation notes for selected history range, overlay count, and explicit return-to-live posture.
  - revision: r1
    date: 2026-03-21
    summary: Clarified live/historical/review/live-trace distinctions and requested/applied/observed overlays.
---
# Graphing History Review and Live Trace Specification [SEC:UDQ-UI-SPEC-004::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-004::1]

This document defines the behavior of the central graphing and review surface across live operation, historical review, explore mode, and explainability use cases.

## 2. Graph Modes [SEC:UDQ-UI-SPEC-004::2]

The graph shall support:
- live follow mode
- user-configurable sliding-window live mode
- whole-session or whole-history review mode
- focused range exploration mode
- live-trace / explainability overlay mode

## 3. Mode Distinction [SEC:UDQ-UI-SPEC-004::3]

Mode changes shall remain explicit. The UI shall make it obvious whether the user is seeing:
- current live-follow data
- detached live sliding-window review
- requested historical retrieval
- mixed historical and live overlays
- explainability overlays on top of live or historical data

## 4. Live Time-Horizon Behavior [SEC:UDQ-UI-SPEC-004::4]

The live graph shall allow the user to configure the active time horizon for sliding-window operation within governed bounds. Expanding the time horizon shall request a broader plotted interval rather than merely stretching the axis while preserving a shorter effective trace history.

## 5. Trace Selection [SEC:UDQ-UI-SPEC-004::5]

The graph shall support:
- named trace selection
- visibility toggles
- grouping or presets where appropriate
- overlay of related raw, derived, requested, and observed signals
- linked legend or trace inventory behavior

## 6. Event and Evidence Overlays [SEC:UDQ-UI-SPEC-004::6]

Where relevant, the graph shall support overlays for:
- events
- alarms
- acknowledgments
- commands
- rule firings
- sequence transitions
- notes or annotations
- selected validation or simulation markers where useful

## 7. Requested / Applied / Observed Views [SEC:UDQ-UI-SPEC-004::7]

Where outputs or governed actions are involved, the graph may show requested, applied, and observed traces or markers. These shall remain visually and semantically distinct.

## 8. Explore and Return-to-Live Behavior [SEC:UDQ-UI-SPEC-004::8]

A user may freely zoom, pan, or brush-select ranges in explore mode. Explore mode shall not silently preserve live follow. Return-to-live shall be one deliberate, durable action that restores the current live-follow posture and selected live horizon.

## 9. Truthful Decimation and Retrieval [SEC:UDQ-UI-SPEC-004::9]

When range size or performance requires downsampling, summarization, or decimation, the graph shall present that honestly. The user shall not be misled into thinking they are seeing every point if they are seeing a summarized representation.

## 10. Range-to-Evidence Linkage [SEC:UDQ-UI-SPEC-004::10]

Selecting a graph range shall be allowed to update the lower evidence pane with related events, alarms, commands, notes, or other evidence where available.

## 11. Bounded Implemented Slice [SEC:UDQ-UI-SPEC-004::11]

The current bounded code already contains graph-mode state scaffolding for live, whole-history, explore, overlay, selected-range, and return-to-live posture. The fuller operator contract defined here remains ahead of complete GUI implementation.


## 11A. Bounded first-bench graph truth additions [SEC:UDQ-UI-SPEC-004::11A]

The current bounded first-bench slice shall keep the active trace semantically linked to:
- signal freshness state
- provenance label and channel metadata
- recent operator/session actions that altered graph posture or session posture
- active alarm posture where relevant to the visible session truth

The bounded graph path does not yet claim full overlay richness, but it shall not present a live-looking trace without the corresponding freshness and provenance context being available at the same shell seam.

## 11B. Historical session review previews [SEC:UDQ-UI-SPEC-004::11B]

The bounded historical-review slice may expose compact saved-session previews such as a bounded sparkline, freshness label, provenance label, operator-note count, and completeness label. Those previews shall remain clearly historical and shall not impersonate a live updating trace.

## 12. Human Review Focus [SEC:UDQ-UI-SPEC-004::12]

A reviewer should quickly confirm that:
- live follow and sliding window are distinct but both supported
- whole-history and explore are explicit
- expanding the live horizon is a real data request expectation, not merely axis stretch
- return-to-live is obvious
- overlays include broader runtime evidence, not only traces
