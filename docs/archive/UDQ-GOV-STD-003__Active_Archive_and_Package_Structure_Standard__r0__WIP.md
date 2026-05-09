---
document_id: UDQ-GOV-STD-003
title: Active Archive and Package Structure Standard
revision: r0
status: WIP
document_class: governance_standard
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-GOV-STD-002"
  - "UDQ-REL-SPEC-001"
revision_history:
  - "r0 | 2026-03-21 | Establishes active/archive separation, frozen package root placement rules, and audit obligations for structure-freeze packages."
---
# Active Archive and Package Structure Standard [SEC:UDQ-GOV-STD-003::0]

## 1. Purpose [SEC:UDQ-GOV-STD-003::1]

This standard freezes the working UniversalDAQ package root structure for pre-implementation hardening packages and establishes explicit placement rules for active documents, archived documents, registries, audit reports, structure skeletons, and future implementation directories.

## 2. Core placement rule [SEC:UDQ-GOV-STD-003::2]

Exactly one active working revision for each controlled `document_id` shall exist under `docs/active/`. Older superseded revisions shall exist under `docs/archive/`. Active truth shall therefore be explicit by placement rather than inferred only from filename revision ordering.

## 3. Root directory structure [SEC:UDQ-GOV-STD-003::3]

```text
<package-root>/
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
├── tests/
├── proof/
├── runtime/
├── tools/
├── README_RUN_AUDIT.md
├── README_HUMAN_PASS.md
├── UDQ_RELEASE_MANIFEST.yaml
├── UDQ_RELEASE_NOTES.md
└── udq_master_audit_v6.py
```

## 4. Directory ownership rules [SEC:UDQ-GOV-STD-003::4]

- `docs/active/` owns the active controlled corpus.
- `docs/archive/` stores prior controlled revisions that remain part of package history.
- `registries/active/` stores the latest machine-readable registry set governing the active corpus.
- `registries/archive/` stores superseded registry revisions.
- `audit_reports/active/` stores the latest audit run for the package baseline.
- `audit_reports/archive/` stores prior audit artifacts.
- `src/`, `tests/`, `proof/`, `runtime/`, and `tools/` are frozen structural locations and may exist as empty skeletons before implementation.

## 5. Forbidden placements [SEC:UDQ-GOV-STD-003::5]

The following are not permitted in a structure-freeze package:

- multiple active revisions of the same `document_id` under `docs/active/`
- archive-only revisions living in `docs/active/`
- active registries stored only in `registries/archive/`
- active audit reports stored only in `audit_reports/archive/`
- implementation modules placed outside the frozen `src/universaldaq/` subtree once implementation begins

## 6. Naming and audit obligations [SEC:UDQ-GOV-STD-003::6]

Active/archive placement does not replace controlled filenames. Controlled filenames, front matter, and cross-reference rules from `UDQ-GOV-STD-001` and `UDQ-GOV-SPEC-002` still apply. The master auditor shall check package structure conformance, active/archive conformance, and active-corpus uniqueness.

## 7. Relationship to future implementation [SEC:UDQ-GOV-STD-003::7]

This standard freezes where future implementation artifacts belong without requiring those implementation artifacts to exist yet. It therefore supports experimentation in package structure now while preserving a clean transition into later runnable code baselines.
