---
document_id: UDQ-IMP-MAP-001
title: Proposed Code Architecture and Module Boundary Map
revision: r0
status: WIP
document_class: implementation_map
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-MAP-001
  - UDQ-GOV-STD-002
  - UDQ-ARCH-NAR-002
revision_history:
  - "r0 | 2026-03-21 | Initial proposed root package structure and future module-boundary map."
---
# Proposed Code Architecture and Module Boundary Map {#imp-map-001.s01}

## 1. Purpose [SEC:UDQ-IMP-MAP-001::1]

This document proposes the future root package structure and module-boundary rules so implementation work begins inside a controlled file architecture.

## 2. Root package target structure [SEC:UDQ-IMP-MAP-001::2]

```text
UDQ-PKG-implementation-<date>-<tag>/
├── udq_master_audit_v5.py
├── README_RUN_AUDIT.md
├── README_HUMAN_PASS.md
├── docs/
├── registries/
├── src/
│   └── universaldaq/
│       ├── app/
│       ├── backend/
│       ├── frontend/
│       ├── adapters/
│       ├── historian/
│       ├── diagnostics/
│       ├── profiles/
│       ├── events/
│       ├── rules/
│       ├── sequences/
│       ├── security/
│       ├── remote/
│       └── common/
├── tests/
│   ├── smoke/
│   ├── conformance/
│   └── fixtures/
├── proof/
│   ├── bundles/
│   ├── logs/
│   └── screenshots/
├── runtime/
│   ├── sample_profiles/
│   ├── sample_configs/
│   └── sample_exports/
└── tools/
    ├── diagnostics/
    ├── traceability/
    └── package_build/
```

## 3. Boundary rules [SEC:UDQ-IMP-MAP-001::3]

- `frontend/` shall not become the hidden owner of runtime truth.
- `backend/` owns authoritative runtime state publication and arbitration orchestration.
- `adapters/` expose capabilities, identity, health, and raw/device-specific transport semantics without leaking protocol detail into ordinary UI workflows.
- `common/` contains shared primitives that do not create circular truth ownership.
- `tests/` shall not substitute for governed proof registries; they support them.
- `tools/` may inspect or build the package but shall not silently mutate controlled source-of-truth artifacts.

## 4. Allowed dependency direction [SEC:UDQ-IMP-MAP-001::4]

Preferred dependency flow:

`common -> adapters/backend domain services -> historian/diagnostics/rules/sequences/security/remote -> app/frontend`

The reverse direction is not allowed except through explicitly defined interfaces.

## 5. Module ownership expectations [SEC:UDQ-IMP-MAP-001::5]

- command arbitration belongs to backend-owned output services,
- signal quality semantics belong to signal/backend services,
- session/profile restore belongs to profile services and app orchestration rather than widget-local ad hoc code,
- event/alarm history belongs to historian/event services,
- UI widgets render backend-authored truth and local interaction state but do not author runtime truth.

## 6. Handoff note [SEC:UDQ-IMP-MAP-001::6]

This file structure is proposed and governed for transition planning. Future implementation packages should either conform to it or revise this document first.
