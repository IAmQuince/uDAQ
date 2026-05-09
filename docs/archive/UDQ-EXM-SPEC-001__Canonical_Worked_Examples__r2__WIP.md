---
document_id: "UDQ-EXM-SPEC-001"
title: "Canonical Worked Examples"
revision: "r2"
status: "WIP"
document_class: "example_spec"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-SPEC-005"
  - "UDQ-REQ-MAT-001"
supersedes:
  - "UDQ-EXM-SPEC-001__Canonical_Worked_Examples__r1__WIP.md"
revision_history:
  - "r2 | 2026-03-21 | Expanded worked examples so the governance layer can attach execution-contract entries and invariants to exact scenarios."
  - "r1 | 2026-03-21 | First canonical examples introduced."
---
# Canonical Worked Examples [SEC:UDQ-EXM-SPEC-001::0]

    ## 1. Purpose [SEC:UDQ-EXM-SPEC-001::1]

    Canonical worked examples provide exact, governed scenario references that future implementation, tests, runtime monitors, and proof bundles can point to.

    ## 2. Current example set [SEC:UDQ-EXM-SPEC-001::2]

    | Example ID | Title | Governing Requirements | Why it matters |
|---|---|---|---|
| UDQ-EXM-001 | Requested command blocked by interlock before arbitration result is published | UDQ-REQ-ARCH-001, UDQ-REQ-SEC-001, UDQ-REQ-OUT-001 | A user requests an output change, authorization succeeds, an interlock denies apply, the request remains recorded, applied state is not advanced, and the rejection reason is persisted. |
| UDQ-EXM-002 | Requested command accepted, applied, then observed mismatch is surfaced | UDQ-REQ-ARCH-001, UDQ-REQ-OUT-002, UDQ-REQ-EVT-001 | A command request is accepted and applied, but observed feedback does not converge; the mismatch becomes explicit rather than silently collapsing applied and observed state. |
| UDQ-EXM-003 | Workspace restore rebuilds operator context without reasserting machine state | UDQ-REQ-PROF-001, UDQ-REQ-PROF-002, UDQ-REQ-ARCH-002 | A saved workspace restores page layout, graph selections, and trace visibility, while machine outputs and live authority remain untouched. |
| UDQ-EXM-004 | Alarm lifecycle assert acknowledge return-to-normal with historian evidence | UDQ-REQ-EVT-001, UDQ-REQ-EVT-002, UDQ-REQ-HIS-001, UDQ-REQ-HIS-002 | An alarm asserts, is acknowledged later, then returns to normal; all lifecycle transitions are timestamped and written to the evidence trail. |
| UDQ-EXM-005 | Graph mode separation between live review historical and live trace | UDQ-REQ-UI-003, UDQ-REQ-UI-004, UDQ-REQ-UI-006, UDQ-REQ-HIS-001 | The operator can inspect historical data without presenting it as live, then re-enter live trace mode with explicit UI indication and no history/live conflation. |

    ## 3. Rule of use [SEC:UDQ-EXM-SPEC-001::3]

    Worked examples are not tutorials. They are normative scenario references for the semantic boundaries most likely to drift during implementation.
