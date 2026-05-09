---
document_id: UDQ-EXM-SPEC-001
title: Canonical Worked Examples
revision: r0
status: WIP
document_class: example_spec
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-GLO-001
  - UDQ-GOV-STD-002
  - UDQ-OUT-SPEC-001
  - UDQ-PROF-SPEC-001
  - UDQ-UI-SPEC-004
revision_history:
  - "r0 | 2026-03-21 | Initial issue adding canonical examples for high-risk semantic boundaries."
---
# Canonical Worked Examples {#exm-spec-001.s01}

## 1. Purpose [SEC:UDQ-EXM-SPEC-001::1]

This document provides small authoritative examples for terms and behaviors that are easy to conflate during future implementation.

## 2. Command request vs applied vs observed [SEC:UDQ-EXM-SPEC-001::2]

1. An operator requests Output A = ON.
2. The UI immediately shows a pending/requested indication.
3. Backend arbitration accepts the request after permission, interlock, and ownership checks.
4. Backend publishes applied state = ON.
5. Device readback later confirms observed state = ON.
6. If readback never confirms, the system may show applied = ON and observed = UNKNOWN or MISMATCH.

The example shows that requested, applied, and observed state are separate facts.

## 3. Profile restore vs machine state [SEC:UDQ-EXM-SPEC-001::3]

1. The application reopens and restores a saved workspace layout and selected traces.
2. The UI marks the workspace as restored.
3. Device connectivity is still re-establishing, so live machine state is not yet validated.
4. The restored layout remains useful, but it does not prove the underlying process is in the same state as when the layout was saved.

The example shows that workspace/profile restore is not the same as live machine-state restoration.

## 4. Historical review vs live trace [SEC:UDQ-EXM-SPEC-001::4]

- **Historical review**: the operator scrubs yesterday's event timeline and historian overlays.
- **Live trace**: the operator watches the current rule evaluation chain and ownership path as the system runs.

Both are explainability-oriented, but only the second remains in live runtime posture.

## 5. Alarm acknowledgment [SEC:UDQ-EXM-SPEC-001::5]

1. Alarm A asserts.
2. The operator acknowledges Alarm A.
3. The acknowledgment is recorded with actor, session, and time.
4. The historical record still shows that Alarm A asserted, was acknowledged, and later returned to normal.

Acknowledgment recognizes a condition; it does not erase the fact that the condition happened.
