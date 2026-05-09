---
document_id: UDQ-UI-SPEC-004
title: Graphing History Review and Live Trace Specification
revision: r5
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
  - UDQ-SIG-SPEC-001
  - UDQ-PERF-SPEC-001
  - UDQ-PROF-SPEC-001
supersedes:
  - UDQ-UI-SPEC-004__Graphing_History_Review_and_Live_Trace_Specification__r3__WIP.md
revision_history:
  - revision: r5
    date: 2026-03-28
    summary: Docs-only UI alignment pass. Expanded graphing to any plottable signal class through curated lenses; introduced the SignalRef/TraceBinding/TracePresentation model; added legend, style, alarm-overlay, saved-setup, and autosave requirements; and formalized pyqtgraph-backed performance doctrine for multi-trace and long-range use.
  - revision: r3
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Added explicit live-follow/sliding-window/whole-history/explore semantics, truthful decimation expectations, user-selected time horizon, evidence linking, and richer overlay rules.
---
# Graphing History Review and Live Trace Specification [SEC:UDQ-UI-SPEC-004::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-004::1]

This document defines the behavior of the central graphing and review surface across live operation, historical review, replay/simulation, and explainability use cases.

## 2. Plot-anything Rule [SEC:UDQ-UI-SPEC-004::2]

Any **plottable signal** may be graphed, provided it resolves to a stable signal identity and carries sufficient metadata for truthful display.

Plottable classes may include:
- raw hardware or adapter-backed values
- normalized logical signals
- derived variables
- control-module outputs or watch values
- simulated values
- replayed values
- historical summaries and previews

The graph shall allow this freedom through curated user views rather than one ambiguous mixed object tree.

## 3. Graph Modes [SEC:UDQ-UI-SPEC-004::3]

The graph shall support:
- live follow mode
- user-configurable sliding-window live mode
- whole-session or whole-history review mode
- focused range exploration mode
- replay / simulation mode
- mixed historical/live explainability overlays where truth boundaries remain explicit

## 4. SignalRef, TraceBinding, and TracePresentation [SEC:UDQ-UI-SPEC-004::4]

### 4.1 SignalRef [SEC:UDQ-UI-SPEC-004::4.1]
A SignalRef is the stable graph-facing reference to a plottable signal.

### 4.2 TraceBinding [SEC:UDQ-UI-SPEC-004::4.2]
A TraceBinding defines how a SignalRef is attached to a graph, including pane, axis, visibility, and setup membership.

### 4.3 TracePresentation [SEC:UDQ-UI-SPEC-004::4.3]
A TracePresentation defines the operator-visible style such as color, width, line pattern, marker behavior, highlight behavior, alarm overlay rules, and legend text.

The same SignalRef may appear in multiple graph setups with different TracePresentation settings.

## 5. Curated Browsing Lenses [SEC:UDQ-UI-SPEC-004::5]

The user shall be able to add traces through curated browsing lenses such as:
- Hardware
- Raw
- Logical
- Derived
- Control
- Favorites / Recent
- Saved Sets

Changing between lenses should usually rebind or relabel the same stable signal identity rather than re-acquire data from hardware.

## 6. Saved Graph Setups [SEC:UDQ-UI-SPEC-004::6]

A graph setup is a first-class persisted object that may carry:
- selected traces
- trace ordering
- lens/view choice
- axis assignment
- time horizon
- live/replay/historical context
- legend mode
- trace style properties
- alarm-visual preferences where user-configurable

Saved graph setups shall be savable, loadable, editable, and restorable in-app.

## 7. Trace Style Flexibility [SEC:UDQ-UI-SPEC-004::7]

Per-trace style shall support, where implemented:
- color
- line width
- solid/dashed/dotted style
- point markers and point size
- opacity
- selected-trace highlight
- optional glow/halo
- blinking or pulse behavior under governed conditions
- primary/secondary axis assignment
- legend label override

These settings shall persist as part of the graph setup or profile system.

## 8. Legend Requirements [SEC:UDQ-UI-SPEC-004::8]

The legend shall be interactive and shall support, at minimum:
- show/hide trace
- select/focus trace
- current value and units where appropriate
- quality/freshness indication
- alarm badge / severity indication
- axis indication
- entry to deeper trace-style editing

## 9. Alarm-aware Trace Overlays [SEC:UDQ-UI-SPEC-004::9]

Alarm styling shall be layered over the base trace style. A trace bound to an alarming condition shall remain recognizable while severity becomes visually obvious.

Typical overlay semantics may include:
- warning halo or outline
- high alarm severity edge emphasis
- critical severity outline, pulse, or blink under stricter policy
- legend severity badge

Severity overlays shall not erase operator-selected color or line identity unless a stricter safety policy explicitly requires that.

## 10. Truthful Decimation and Retrieval [SEC:UDQ-UI-SPEC-004::10]

When range size or performance requires downsampling, summarization, or decimation, the graph shall present that honestly. The user shall not be misled into thinking they are seeing every point if they are seeing a summarized representation.

## 11. Performance Doctrine for Graphing [SEC:UDQ-UI-SPEC-004::11]

The current architectural direction retains **pyqtgraph** as the primary graphing engine, but performance shall not be delegated to the library alone.

The graphing path shall therefore separate:
- acquisition cadence
- canonical signal storage
- selection and lens resolution
- rendering cadence

The graphing path shall also prefer:
- bounded live buffers
- multiresolution or decimated caches for long ranges
- rebind/relabel behavior on lens changes instead of full reacquire
- presentation-rate throttling
- trace-count and time-horizon guardrails
- optional performance mode or graceful style simplification under heavy load

## 12. Historical Session Review Previews [SEC:UDQ-UI-SPEC-004::12]

Historical session review may expose compact previews such as bounded sparklines, completeness labels, provenance labels, and note/alarm digests. Those previews shall remain clearly historical and shall not impersonate a live updating trace.

## 13. Human Review Focus [SEC:UDQ-UI-SPEC-004::13]

A reviewer should quickly confirm that:
- any plottable signal can be graphed through curated views
- SignalRef, TraceBinding, and TracePresentation remain separate concepts
- trace styling, legend behavior, and alarm overlays are first-class and persisted
- pyqtgraph is treated as the rendering engine, not as the whole performance strategy
- long-range and many-trace graphing remain bounded and truth-preserving

## 2A. Curated Signal Lenses [SEC:UDQ-UI-SPEC-004::2A]

The graphing surface shall permit the operator to add any plottable signal through curated signal lenses rather than a single mixed tree. The minimum supported lenses are:
- Hardware
- Raw
- Logical
- Derived
- Control
- Saved Sets

Switching between these lenses should, where possible, rebind or relabel existing canonical signal identities rather than reacquire hardware data.

## 4A. Trace Presentation Persistence [SEC:UDQ-UI-SPEC-004::4A]

Trace presentation shall be modeled separately from signal identity and trace binding. Presentation settings that must be persistable include, at minimum:
- color
- line width
- solid / dashed / dotted pattern
- marker visibility and size
- opacity
- selection highlight
- second-axis assignment
- alarm-overlay policy
- legend label behavior

All user-facing graph settings shall be editable inside the application. Autosave for graph and trace settings shall be user-togglable.

## 4B. Alarm Overlay Doctrine [SEC:UDQ-UI-SPEC-004::4B]

Alarm visualization shall be applied as an overlay on top of base trace style rather than destructively replacing operator-selected style. Warning-level conditions should be visually distinct from high and critical alarm states. When performance pressure requires simplification, the graphing layer may degrade ornamental effects while preserving base identity, severity visibility, and truthfulness.

## 7A. pyqtgraph Performance Doctrine [SEC:UDQ-UI-SPEC-004::7A]

pyqtgraph remains the selected plotting engine, but rendering performance remains an application responsibility. The implementation shall separate acquisition, canonical storage, signal selection, and rendering. Multi-resolution or decimated representations shall be used for medium and long historical windows, and style-heavy overlays may be simplified under load while preserving truth, selection emphasis, and alarm visibility.


## 2026-03-30 documentation closeout addendum — current trace feature status
The current package line should be interpreted as follows.

### Implemented now
- line color
- line width
- solid / dashed / dotted pattern
- marker style
- marker size
- immediate redraw on style change
- graph presentation modes `Primary`, `PiP`, and `Hidden`
- direct PiP recovery through graph-mode controls rather than only through layout reset

### Preview-only or deferred
- true live secondary-axis rendering remains preview-only in the current package line
- glow / halo / blink effects remain preview-only or deferred rather than fully live style effects
- advanced multi-axis behavior is deferred

This feature-status matrix is authoritative for the current review package and should be preferred over older UI prose that implied broader graph-style completeness.
