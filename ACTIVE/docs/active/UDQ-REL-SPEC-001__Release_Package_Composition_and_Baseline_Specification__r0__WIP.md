---
document_id: UDQ-REL-SPEC-001
title: Release Package Composition and Baseline Specification
revision: r0
status: WIP
classification:
  domain: REL
  type: SPEC
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-SCM-STD-001
- UDQ-AUD-SPEC-001
- UDQ-GOV-LOG-001
- UDQ-GOV-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Release Package Composition and Baseline Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-21 | WIP | Initial issue defining the minimum composition, structure, and baseline expectations for governed UniversalDAQ send-out packages. |

# 1. Purpose [SEC:UDQ-REL-SPEC-001::1]

This specification defines what shall be inside a proper UniversalDAQ send-out package and how that package shall identify its baseline, truth sources, and review posture.

# 2. Scope [SEC:UDQ-REL-SPEC-001::2]

This specification applies to zipped and unpacked send-out packages for:

- documentation baselines
- pre-code planning baselines
- implementation review packages
- release candidates
- released internal or external delivery bundles

# 3. Package Classes [SEC:UDQ-REL-SPEC-001::3]

UniversalDAQ packages shall declare one of the following package classes:

- `DOC_BASELINE`
- `PRECODE_BASELINE`
- `IMPLEMENTATION_REVIEW`
- `RELEASE_CANDIDATE`
- `RELEASED_PACKAGE`

The declared package class determines which artifacts are mandatory and how strict the audit posture shall be.

# 4. Required Top-Level Package Contents [SEC:UDQ-REL-SPEC-001::4]

Every governed send-out package shall include at package root:

1. package-root audit tool
2. release manifest
3. release notes/update summary
4. top-level README or equivalent launch guidance
5. the delivered content root(s) referenced by the manifest
6. an `audit_reports/` location or a defined output location for generated audit artifacts

Where controlled documents are included, the package shall also include:

- controlled document index
- active document registry
- active cross-reference registry
- requirement registry when requirements are in scope

# 5. Required Baseline Identification [SEC:UDQ-REL-SPEC-001::5]

Every package shall declare:

- package release ID
- package class
- code baseline ID or explicit `NO_CODE_SCOPE`
- documentation baseline ID or explicit `NO_DOC_SCOPE`
- package status
- issue date
- comparison baseline, if any
- auditor version expected at package root

# 6. Required Structure Expectations [SEC:UDQ-REL-SPEC-001::6]

## 6.1 Structure Rule [SEC:UDQ-REL-SPEC-001::6.1]

The package shall be internally coherent and auditable after unzip without path guessing. The manifest shall identify the intended relative locations of:

- audit tool
- manifest
- release notes
- document/control artifacts
- source-of-truth code files
- major content roots

## 6.2 Predictable Layout [SEC:UDQ-REL-SPEC-001::6.2]

A recommended structure is:

- package root
  - audit tool
  - manifest
  - release notes
  - README
  - docs or controlled-doc roots
  - source or implementation roots
  - audit_reports

Alternative structures are allowed only if the manifest states them clearly and the package-root audit tool can validate them.

# 7. Required Manifest Contents [SEC:UDQ-REL-SPEC-001::7]

The release manifest shall include, at minimum:

- package identity block
- baseline identity block
- compatibility statement block
- source-of-truth file list
- included artifact inventory
- required directories/files list
- package audit expectations
- known exceptions/deviations if any

# 8. Required Release Notes Contents [SEC:UDQ-REL-SPEC-001::8]

Release notes shall include, at minimum:

- package release ID
- comparison point
- summary of changes
- added/changed/removed items
- reviewer attention items
- known issues/limitations
- audit summary
- compatibility notes

# 9. Documentation-Inclusive Packages [SEC:UDQ-REL-SPEC-001::9]

Where controlled documentation is part of the package, the package shall include the active controlled revisions referenced by the manifest, not an undefined mixture of obsolete and active drafts. The manifest shall identify which controlled index revision is authoritative for the package.

# 10. Code-Inclusive Packages [SEC:UDQ-REL-SPEC-001::10]

Where code is included, the package shall identify:

- primary entry point(s)
- authoritative backend/frontend modules
- configuration/schema source files
- smoke-test or launch scripts if present
- known required runtime dependencies
- whether the package is intended for execution, review, or reference only

# 11. Package Truth and Audit Position [SEC:UDQ-REL-SPEC-001::11]

The package-root auditor shall be treated as the immediate package truth-check. A proper send-out package shall either:

- pass the required audit profile for its class, or
- carry an explicit documented exception stating why the package is intentionally incomplete

Undeclared audit failure shall be treated as package incompleteness.

# 12. Exceptions and Deviations [SEC:UDQ-REL-SPEC-001::12]

If a package intentionally omits a normally required artifact, the manifest and release notes shall both declare:

- the omitted artifact
- the reason
- the impact
- the mitigation or next expected package

# 13. Minimum Package Matrix by Class [SEC:UDQ-REL-SPEC-001::13]

| Artifact | DOC_BASELINE | PRECODE_BASELINE | IMPLEMENTATION_REVIEW | RELEASE_CANDIDATE | RELEASED_PACKAGE |
|---|---|---|---|---|---|
| Auditor at root | Required | Required | Required | Required | Required |
| Manifest | Required | Required | Required | Required | Required |
| Release notes | Required | Required | Required | Required | Required |
| Controlled index | Required if docs included | Required if docs included | Required if docs included | Required if docs included | Required if docs included |
| Registries | Required if docs included | Required if docs included | Required if docs included | Required if docs included | Required if docs included |
| Source-of-truth file list | Optional | Optional | Required if code included | Required | Required |
| Compatibility statement | Required | Required | Required | Required | Required |
| Audit output from current package | Optional | Optional | Recommended | Required | Required |

# 14. Anti-Patterns [SEC:UDQ-REL-SPEC-001::14]

The following are prohibited:

- sending a package with no manifest
- sending a package with no release notes
- placing the auditor in a hidden nested location while expecting it to govern the package
- mixing unrelated baselines into one package without declaring that mix
- package contents that contradict the manifest
- release notes that omit major behavior changes

# 15. Downstream Obligations [SEC:UDQ-REL-SPEC-001::15]

This specification shall govern:

- release manifest template content in `UDQ-REL-TPL-001`
- release notes/update summary content in `UDQ-REL-TPL-002`
- package-root auditor expectations
- future package composition and delivery discipline
