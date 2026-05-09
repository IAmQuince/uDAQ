---
document_id: UDQ-UI-DEVFLOW-001
title: Device Discovery Onboarding and Known Device UX
revision: r1
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-DEV-SPEC-001
  - UDQ-UI-ARCH-001
  - UDQ-UI-SPEC-001
  - UDQ-UI-SPEC-006
supersedes:
  - UDQ-UI-DEVFLOW-001__Device_Discovery_Onboarding_and_Known_Device_UX__r0__WIP.md
---

# Device Discovery Onboarding and Known Device UX [SEC:UDQ-UI-DEVFLOW-001::0]

## 1. Purpose [SEC:UDQ-UI-DEVFLOW-001::1]

This document defines the user experience for discovering devices, onboarding them into UniversalDAQ, recognizing known devices, and handing newly available signals or capabilities into the broader workspace model.

## 2. Canonical Flow [SEC:UDQ-UI-DEVFLOW-001::2]

The canonical flow is:
1. discover or connect device
2. identify capability and stable identity
3. confirm or create point/binding candidates
4. expose signals and commandable capabilities
5. hand relevant sources into the Control workspace for variable or action authoring
6. preserve auditability and reconnect/remap posture

## 3. Quick Start [SEC:UDQ-UI-DEVFLOW-001::3]

Quick start shall favor recognizable device identity, safe defaults, and minimal friction. It shall not force ordinary users into raw protocol detail on first contact.

## 4. Advanced Setup [SEC:UDQ-UI-DEVFLOW-001::4]

Advanced setup may expose protocol-specific capability, raw address/detail, or support-pack nuance where needed for commissioning or service.

## 5. Known-Device Rule [SEC:UDQ-UI-DEVFLOW-001::5]

Known devices shall be recognized by stable identity rather than by a fragile positional assumption.

## 6. Support-Tier Truthfulness [SEC:UDQ-UI-DEVFLOW-001::6]

The UI shall remain honest about whether support for a device family is native, support-pack-provided, experimental, or unavailable.

## 7. Binding and Variables [SEC:UDQ-UI-DEVFLOW-001::7]

Onboarding does not end with connection. Newly available signals and capabilities shall flow cleanly into:
- Variables in the Control workspace
- Actions / Bindings in the Control workspace
- System diagnostics and identity tracking

The UI shall not assume that the device onboarding surface is also the long-term authoring surface.

## 8. Multi-Instance Devices [SEC:UDQ-UI-DEVFLOW-001::8]

Same-family multi-instance devices shall remain distinguishable by stable identity and usage context.

## 9. Recovery and Remap [SEC:UDQ-UI-DEVFLOW-001::9]

When identity ambiguity or remap is needed, the UI shall preserve the operator’s ability to review what changed and what authored assets may be affected.

## 10. Current Package Alignment Note [SEC:UDQ-UI-DEVFLOW-001::10]

This docs-only run aligns onboarding language with the newer Run / Control / Review / System workspace model. Device onboarding remains primarily a System concern that feeds Control rather than a hidden control-authoring environment by itself.
