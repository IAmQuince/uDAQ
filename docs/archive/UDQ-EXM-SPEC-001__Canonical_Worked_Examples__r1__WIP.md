---
document_id: UDQ-EXM-SPEC-001
title: Canonical Worked Examples
revision: r1
status: WIP
document_class: example_spec
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-STD-002"
  - "UDQ-OUT-SPEC-001"
  - "UDQ-PROF-SPEC-001"
  - "UDQ-UI-SPEC-004"
  - "UDQ-EVT-SPEC-001"
supersedes:
  - "UDQ-EXM-SPEC-001__Canonical_Worked_Examples__r0__WIP.md"
revision_history:
  - "r1 | 2026-03-21 | Expanded the canonical examples to support subsystem closure and future implementation entry."
  - "r0 | 2026-03-21 | Initial issue adding canonical examples for high-risk semantic boundaries."
---
# Canonical Worked Examples [SEC:UDQ-EXM-SPEC-001::0]

## 1. Purpose [SEC:UDQ-EXM-SPEC-001::1]

This document provides small authoritative examples for terms and behaviors that are easy to conflate during future implementation.

## 2. Command accepted and confirmed [SEC:UDQ-EXM-SPEC-001::2]

1. An operator requests Output A = ON.
2. The UI shows **requested = ON, applied = OFF/unknown, observed = OFF/unknown**.
3. Backend authorization and arbitration accept the request.
4. Backend publishes **applied = ON**.
5. Device readback later confirms **observed = ON**.
6. Historian evidence records the request, arbitration result, applied publication, and observed confirmation as linked but distinct facts.

## 3. Command blocked by interlock [SEC:UDQ-EXM-SPEC-001::3]

1. A user requests Pump Start.
2. A permissive is false, so arbitration does not allow the command to proceed.
3. The system records **requested = START**, **applied = unchanged**, **observed = stopped**, with a **blocked/interlocked** explanation.
4. The user can review both the request and the reason it was not applied.

## 4. Applied-versus-observed mismatch [SEC:UDQ-EXM-SPEC-001::4]

1. The platform publishes **applied = valve open** after issuing the command.
2. Readback remains **observed = closed** after the confirmation window.
3. The UI and historian show a mismatch rather than silently rewriting one state to the other.
4. Diagnostics and event history remain attributable to the same command chain.

## 5. Profile restore versus machine state [SEC:UDQ-EXM-SPEC-001::5]

1. The application reopens and restores a saved workspace layout and selected traces.
2. The UI marks the workspace as restored.
3. Backend connectivity is still re-establishing, so live machine state is not yet validated.
4. The restored layout remains useful, but it does not prove the underlying process is in the same state as when the layout was saved.

## 6. Historical review versus live trace [SEC:UDQ-EXM-SPEC-001::6]

- **Historical review**: the operator scrubs yesterday's event timeline and historian overlays.
- **Review mode**: the operator is intentionally in evidence-exploration posture, even if a live connection still exists.
- **Live trace**: the operator watches the current rule evaluation chain and ownership path as the system runs.

These are related, but only the third remains in live runtime posture.

## 7. Alarm acknowledgment [SEC:UDQ-EXM-SPEC-001::7]

1. Alarm A asserts.
2. The operator acknowledges Alarm A.
3. The acknowledgment is recorded with actor, session, and time.
4. The historical record still shows that Alarm A asserted, was acknowledged, and later returned to normal.

Acknowledgment recognizes a condition; it does not erase the fact that the condition happened.
