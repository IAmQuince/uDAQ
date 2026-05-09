---
document_id: UDQ-IMP-MAP-001
title: Frozen Package Structure and Module Boundary Standard
revision: r1
status: WIP
document_class: implementation_map
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-003"
  - "UDQ-GOV-STD-002"
  - "UDQ-ARCH-NAR-002"
supersedes:
  - "UDQ-IMP-MAP-001__Proposed_Code_Architecture_and_Module_Boundary_Map__r0__WIP.md"
revision_history:
  - "r1 | 2026-03-21 | Promoted the proposed structure to a frozen package/module boundary standard for structure-freeze packages."
  - "r0 | 2026-03-21 | Initial proposed root package structure and future module-boundary map."
---
# Frozen Package Structure and Module Boundary Standard [SEC:UDQ-IMP-MAP-001::0]

## 1. Purpose [SEC:UDQ-IMP-MAP-001::1]

This document freezes the package root structure and the intended module-boundary map that future implementation work shall use. It is the implementation-facing companion to `UDQ-GOV-STD-003`.

## 2. Frozen root structure [SEC:UDQ-IMP-MAP-001::2]

```text
UDQ-PKG-<date>-<tag>/
├── udq_master_audit_v6.py
├── README_RUN_AUDIT.md
├── README_HUMAN_PASS.md
├── UDQ_RELEASE_MANIFEST.yaml
├── UDQ_RELEASE_NOTES.md
├── docs/
│   ├── active/
│   └── archive/
├── registries/
│   ├── active/
│   └── archive/
├── audit_reports/
│   ├── active/
│   └── archive/
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
- `backend/` owns authoritative runtime state publication, arbitration outcomes, and current machine-facing coordination.
- `adapters/` own protocol/device translation and capability exposure, not business logic.
- `historian/` owns evidence persistence and retrieval, not live authority.
- `profiles/` own persistence of local/session/configuration artifacts, not direct machine-state reassertion.
- `events/` own event/alarm lifecycle coordination.
- `rules/` and `sequences/` own governed runtime logic that emits requests or state transitions while remaining subordinate to authorization and arbitration boundaries.
- `security/` owns role and authorization policy evaluation.
- `remote/` owns remote surface coordination and session boundary handling.
- `common/` contains shared types/utilities that do not smuggle cross-layer ownership.

## 4. Prohibited drift patterns [SEC:UDQ-IMP-MAP-001::4]

- UI-only state becoming the de facto machine state
- protocol adapters directly implementing higher-level arbitration policy
- historian or export code becoming the live authority source
- rules or sequences bypassing output arbitration/authorization
- remote surfaces silently assuming local capability parity

## 5. Implementation-entry rule [SEC:UDQ-IMP-MAP-001::5]

Future code should begin only inside this frozen structure. New implementation modules should declare their owning requirements, governed documents, and boundary assumptions so package-level traceability remains auditable.
