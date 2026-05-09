---
document_id: "UDQ-EXM-SPEC-001"
title: "Canonical Worked Examples"
revision: "r3"
status: "WIP"
document_class: "example_spec"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-SPEC-005"
  - "UDQ-REQ-MAT-001"
supersedes:
  - "UDQ-EXM-SPEC-001__Canonical_Worked_Examples__r2__WIP.md"
revision_history:
  - "r3 | 2026-03-21 | Expanded the canonical examples into direct implementation-entry scenario references with expected invariant and evidence links."
  - "r2 | 2026-03-21 | Expanded worked examples so the governance layer could attach execution-contract entries and invariants to exact scenarios."
---
# Canonical Worked Examples [SEC:UDQ-EXM-SPEC-001::0]

## 1. Purpose [SEC:UDQ-EXM-SPEC-001::1]
Canonical worked examples are governed scenario references for the semantic boundaries most likely to drift during implementation.

## 2. Current example set [SEC:UDQ-EXM-SPEC-001::2]
| Example ID | Title | Governing Requirements | Expected invariant emphasis | Expected evidence |
|---|---|---|---|---|
| `UDQ-EXM-001` | Requested command blocked before apply | UDQ-REQ-ARCH-001, UDQ-REQ-OUT-001, UDQ-REQ-SEC-001 | requested != applied; authorization and arbitration occur before apply | request event, rejection reason, no-apply assertion |
| `UDQ-EXM-002` | Requested command accepted, applied, then observed mismatch is surfaced | UDQ-REQ-ARCH-001, UDQ-REQ-OUT-002, UDQ-REQ-EVT-001 | applied != observed; mismatch path explicit | command trace, mismatch event, timing basis |
| `UDQ-EXM-003` | Workspace/profile restore rebuilds operator context without reasserting machine state | UDQ-REQ-PROF-001, UDQ-REQ-PROF-002, UDQ-REQ-ARCH-002 | restore != machine-state apply | restore-origin event, no-write assertion, rebuilt workspace trace |
| `UDQ-EXM-004` | Alarm lifecycle assert, acknowledge, return-to-normal with evidence | UDQ-REQ-EVT-001, UDQ-REQ-EVT-002, UDQ-REQ-HIS-001 | lifecycle ordering; acknowledgment does not erase truth | alarm lifecycle events, acknowledgment actor/time, historian trace |
| `UDQ-EXM-005` | Graph mode separation between live, review, history, and live trace | UDQ-REQ-UI-003, UDQ-REQ-UI-004, UDQ-REQ-UI-006, UDQ-REQ-HIS-002 | review/history/live-trace != live runtime state | mode-change trace, screenshots, review/live return trace |

## 3. Rule of use [SEC:UDQ-EXM-SPEC-001::3]
These examples are normative. The first code sprint should produce scenario-harness placeholders that point to these IDs directly.
