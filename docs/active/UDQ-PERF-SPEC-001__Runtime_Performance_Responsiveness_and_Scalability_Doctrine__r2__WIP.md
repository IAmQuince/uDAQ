---
document_id: UDQ-PERF-SPEC-001
title: Runtime Performance, Responsiveness, and Scalability Doctrine
revision: r2
status: WIP
document_class: performance_spec
owner: UniversalDAQ
depends_on:
  - "UDQ-DEV-SPEC-001"
  - "UDQ-LIFECYCLE-SPEC-001"
  - "UDQ-HIS-SPEC-001"
  - "UDQ-OUT-SPEC-001"
  - "UDQ-GOV-SPEC-005"
  - "UDQ-UI-SPEC-004"
revision_history:
  - "r2 | 2026-03-28 | Docs-only UI alignment pass: added graphing/rendering doctrine, multiresolution history expectations, rebind-vs-reacquire rules for browse-lens switching, and style/performance guardrails for the pyqtgraph-based operator surface."
  - "r1 | 2026-03-26 | Added bounded historian-tier and acceptance-automation posture so routine validation can stay self-demonstrating and low-friction."
---
# Runtime Performance, Responsiveness, and Scalability Doctrine

## 1. Purpose

Define the performance posture for UniversalDAQ so responsiveness, bounded-memory behavior, and truth-preserving degradation are governed properties of the architecture rather than later optimization work.

## 2. Core doctrine

### 2.1 Truth-preserving performance
Performance measures shall not silently falsify runtime truth. If work must be decimated, coalesced, deferred, or dropped, the system shall preserve the correctness of critical device, signal, variable, logic, and governed-output state.

### 2.2 Rate separation
The system shall separate at least these runtime cadences where applicable:
- acquisition / polling
- point normalization
- signal and variable evaluation
- logic evaluation
- historian batching
- UI refresh and plotting
- heavy diagnostics and export generation

### 2.3 Bounded-memory posture
Live runtime paths shall prefer bounded buffers, rolling windows, capped caches, and explicit archival handoff rather than unbounded in-memory growth.

### 2.4 Incremental propagation
A single changed point or signal shall update only affected downstream bindings, variables, logic blocks, and outputs unless a broader recompute is explicitly justified and measured.

### 2.5 Overload priorities
When runtime load rises, UniversalDAQ shall degrade noncritical presentation fidelity before it degrades critical safety, authorization, identity, or logic-truth paths.

## 3. Graphing and rendering doctrine

### 3.1 Separation rule
Graphing performance shall be managed by separating:
- acquisition
- canonical signal storage
- signal selection / browse-lens resolution
- rendering cadence

### 3.2 Rebind versus reacquire
Switching between Hardware, Raw, Logical, Derived, Control, or Saved-Set views should usually rebind or relabel existing signal references rather than trigger fresh hardware acquisition.

### 3.3 Multiresolution history
The plotting path shall prefer:
- bounded full-resolution live buffers for short windows
- lightly decimated medium-range retrievals
- aggressively summarized long-range views where needed

### 3.4 Presentation cadence
The graph shall refresh on a presentation cadence rather than one redraw per raw sample arrival whenever rates make that necessary.

### 3.5 Style guardrails
Rich styling such as thick lines, dashed lines, glow/halo effects, blinking alarm treatments, and many live legend updates shall be treated as performance-sensitive features. The system may simplify or throttle those treatments under heavy load rather than allow them to silently degrade core responsiveness.

## 4. Current graph-engine note

The current UI doctrine retains **pyqtgraph** as the primary graphing engine. Built-in clipping, downsampling, and related features may be used, but UniversalDAQ shall not assume the library alone solves large-history or many-trace performance. Performance remains an architectural responsibility of the application.

## 5. Human Review Focus

A reviewer should quickly confirm that:
- graphing performance is treated as an architecture concern rather than a widget-only concern
- browse-lens switching is designed as rebind/relabel work where possible
- multiresolution history and bounded live buffers are expected from the start
- rich trace styling is acknowledged as performance-sensitive rather than free
