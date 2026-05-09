---
document_id: UDQ-HIS-SPEC-001
title: Historian, Events, and Evidence Specification
revision: r5
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
  - "UDQ-SIG-SPEC-001"
  - "UDQ-OUT-SPEC-001"
  - "UDQ-SEQ-SPEC-001"
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-STD-002"
supersedes:
  - "UDQ-HIS-SPEC-001__Historian_Events_and_Evidence_Specification__r3__WIP.md"
revision_history:
  - "r5 | 2026-03-26 | Added populated specimen historian expectations, read-only review summary posture, and acceptance criteria for non-zero hot/warm history content."
  - "r4 | 2026-03-26 | Added bounded history-tier summaries, deterministic replay-report posture, and one-command acceptance automation as the next layer on top of the durable runtime evidence path."
  - "r3 | 2026-03-22 | Updated in place to reflect manifest-backed historian/export assembly, review artifact serialization, and bounded export diagnostics on top of shell-session evidence records."
  - "r2 | 2026-03-21 | Subsystem reconciliation pass: clarified live-vs-historical evidence semantics and review/live-trace boundaries."
---
# Historian, Events, and Evidence Specification [SEC:UDQ-HIS-SPEC-001::0]

## 1. Purpose [SEC:UDQ-HIS-SPEC-001::1]

This specification defines how UniversalDAQ shall record, preserve, expose, and export runtime history, events, and evidence.

## 2. Governing principle [SEC:UDQ-HIS-SPEC-001::2]

Historian records, event records, and review bundles are evidence surfaces; they are not the same thing as current backend truth.

## 3. Bounded implemented slice [SEC:UDQ-HIS-SPEC-001::3]

The current bounded implementation now includes bundle and export assembly across:
- restore evidence records
- command traces
- alarm lifecycle records
- shell-session evidence such as page changes, trace visibility changes, overlay changes, range selection, export invocation, and return-to-live invocation
- optional profile snapshots and diagnostic payloads as serialized artifacts inside the export result

## 4. Review posture [SEC:UDQ-HIS-SPEC-001::4]

Historical review mode and live trace mode may share overlays, but they remain semantically different operating postures.
The current bounded code preserves that distinction in graph mode state, shell-facing view models, and export scope summary.

## 5. Manifest-backed evidence [SEC:UDQ-HIS-SPEC-001::5]

Historian exports are now expected to produce:
- a deterministic manifest describing included artifacts
- omission notes when a scope excludes a source family
- integrity warnings when a source family is enabled but empty
- review-oriented summaries that distinguish raw evidence from interpreted presentation

## 6. Human review focus [SEC:UDQ-HIS-SPEC-001::6]

A human pass should verify that bundle contents can explain shell-level review and export actions without implying that those actions themselves are current backend truth.

## 7. Canonical runtime evidence route [SEC:UDQ-HIS-SPEC-001::7]
The lifecycle review bundle now carries an additive canonical runtime evidence route that organizes the already-existing runtime surfaces into one coherent bundle. This route does not replace deeper raw evidence; it renders one bounded path through it.

## 8. Evidence survivability and recovery addendum [SEC:UDQ-HIS-SPEC-001::8]
The current bounded sprint adds a governed runtime-journal durability scaffold on top of the existing evidence route. In bounded form, this means:
- session-scoped journal segments with ordered `sequence_id`
- manifest-backed segment enumeration for later replay and audit
- checkpoint files that record the last committed journal sequence plus a hashed payload
- bounded tail-replay capability after the last committed checkpoint

This is intentionally a foundation layer, not a claim that the platform already has a full mature long-run historian.


## 9. Historian depth and acceptance automation addendum [SEC:UDQ-HIS-SPEC-001::9]
The current bounded continuation pass adds a reviewer-facing historian depth layer without claiming full historian maturity. In bounded form, this means:
- hot / warm / cold history summaries over in-memory and persisted evidence surfaces
- session artifact inventory and segment-index reporting for the governed journal lane
- deterministic replay reports derived from checkpoint payload plus journal tail projection
- one-command acceptance automation that emits a machine-readable and human-readable proof bundle

This remains a bounded usability and proof layer, not a claim of full long-run historian or workbench completion.


## 10. Populated specimen historian and reviewability addendum [SEC:UDQ-HIS-SPEC-001::10]
The next bounded strengthening layer is not broader device scope; it is meaningful specimen historian population and read-only reviewability. In bounded form, this now means:
- the acceptance lane shall populate non-zero sample rows in the hot tier
- the acceptance lane shall populate non-zero variable and cycle rows in the warm tier
- the acceptance lane shall preserve cold persisted journal/checkpoint authority underneath those populated summaries
- the package shall emit a read-only review summary artifact so the operator can inspect a session without manual folder archaeology

This remains bounded to the current specimen lane and does not claim generalized historian/workbench completion.
