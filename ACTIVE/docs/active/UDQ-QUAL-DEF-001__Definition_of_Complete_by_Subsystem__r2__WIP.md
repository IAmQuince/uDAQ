---
document_id: UDQ-QUAL-DEF-001
title: Definition of Complete by Subsystem
revision: r2
status: WIP
classification:
  domain: QUAL
  type: DEF
  sequence: '001'
effective_date: '2026-03-22'
authoring_context: UniversalDAQ
depends_on:
- UDQ-ARCH-NAR-001
- UDQ-ARCH-NAR-002
- UDQ-GOV-STD-001
- UDQ-REQ-MAT-001
- UDQ-UI-ARCH-001
- UDQ-UI-MOD-001
- UDQ-UI-NAR-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Definition of Complete by Subsystem

## Revision History

| Revision | Date | Author | Summary |
|---|---|---|---|
| r2 | 2026-03-22 | OpenAI | Updated in place to tighten completion language around lifecycle, binding, variable, and reconciliation readiness in addition to earlier historian/export depth. |
| r1 | 2026-03-21 | OpenAI | Revised to incorporate the UI foundation documents, strengthen frontend completion criteria, add explainability/authority/restore expectations, and align subsystem completion with the updated requirements matrix. |
| r0 | 2026-03-21 | OpenAI | Initial controlled working draft establishing subsystem-level definition of complete for UniversalDAQ. |

## 1. Purpose [SEC:UDQ-QUAL-DEF-001::1]

This document defines what “complete” means for each major subsystem of UniversalDAQ. It exists to prevent false completion, partial implementation drift, UI-only completion claims, backend-only completion claims, and release decisions based on intuition rather than explicit readiness criteria.

## 2. General completion gates [SEC:UDQ-QUAL-DEF-001::2]

A subsystem is not complete merely because code exists. It must satisfy semantic closure, interface clarity, error-handling posture, observability, persistence discipline where relevant, explainability, non-regression protection, reviewable evidence, and an explicit performance posture for any runtime-sensitive path.

## 3. Cross-subsystem minimum gates [SEC:UDQ-QUAL-DEF-001::3]

### 3.1 Semantic closure gate [SEC:UDQ-QUAL-DEF-001::3.1]
The subsystem must have controlled vocabulary, explicit role, and clear authority boundaries.

### 3.2 Interface gate [SEC:UDQ-QUAL-DEF-001::3.2]
The subsystem must expose stable interfaces or explicitly controlled provisional interfaces. Hidden coupling and opportunistic access to internal state are not acceptable as completion.

### 3.3 Evidence gate [SEC:UDQ-QUAL-DEF-001::3.3]
At minimum, completion requires a reviewable combination of requirement references, implementation references, smoke-test or diagnostic results, runtime evidence such as logs/screenshots/exported files/event traces, and known limitation disclosure.

## 4. Subsystem Definitions of Complete [SEC:UDQ-QUAL-DEF-001::4]

### 4.1 Historian / Event / Evidence [SEC:UDQ-QUAL-DEF-001::4.1]
**Working complete** when live trends, sliding-window review, whole-session review, explicit return-to-live behavior, event logging, command audit, manifest-backed export/review pathways, and deterministic omission/warning handling are present and unambiguous.

**Release complete** when rollover/retention paths are tested, historical review is distinguishable from live review, evidence exports are reproducible, manifests describe included artifacts clearly, and diagnostic/profile payload inclusion is governed.

**Not complete if** review mode is ambiguous, events cannot be correlated to state transitions, evidence is too weak to reconstruct behavior, or exports exist without manifest/provenance clarity.

### 4.2 Persistence / Profiles / Restore [SEC:UDQ-QUAL-DEF-001::4.2]
**Working complete** when layout/session/profile persistence boundaries are explicit; local continuity can be restored safely; machine truth is not conflated with UI continuity; corrupt persistence is bounded.

**Release complete** when restore tests cover startup, reconnect, missing/corrupt persisted data, profile switching, and export-safe snapshot serialization with evidence.

**Not complete if** restoring UI state silently reissues machine-state assumptions or manual control intent.

### 4.3 Diagnostics / Service / Dependency Visibility [SEC:UDQ-QUAL-DEF-001::4.3]
**Working complete** when health surfaces exist for backend, device/protocol, historian, publication, command path, lifecycle inventory, binding integrity, and reconciliation posture.

**Release complete** when diagnostic harnesses and dependency reports are runnable and their outputs are packageable.

**Not complete if** failures require guesswork or service posture is invisible.

### 4.4 Lifecycle / Binding / Variable / Reconciliation [SEC:UDQ-QUAL-DEF-001::4.4]
**Working complete** when stable-vs-transient identity is explicit; device, point, signal, variable, and logical-output states are modeled distinctly; same-family multi-instance devices remain separable; reconnect/remap outcomes are reviewable; and missing critical inputs do not silently collapse to nominal values.

**Release complete** when reconnect, port migration, ambiguity review, degraded-source propagation, variable reevaluation, and safe restore behaviors are covered by tests and diagnostics.

**Not complete if** logic still depends directly on raw hardware channel naming, port change alone redefines identity, signal loss produces silent false continuity, or the hot path remains unmeasured and structurally unbounded.

## 5. Notes [SEC:UDQ-QUAL-DEF-001::5]

This revision keeps the bounded, non-actuating posture intact while making lifecycle/binding/variable/reconciliation completeness more concrete and reviewable.
