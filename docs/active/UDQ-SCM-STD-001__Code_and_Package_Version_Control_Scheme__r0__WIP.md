---
document_id: UDQ-SCM-STD-001
title: Code and Package Version Control Scheme
revision: r0
status: WIP
classification:
  domain: SCM
  type: STD
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-GOV-STD-001
- UDQ-GOV-SPEC-002
- UDQ-QUAL-SPEC-002
- UDQ-AUD-SPEC-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Code and Package Version Control Scheme

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-21 | WIP | Initial issue defining code baseline IDs, package release IDs, revision lineage, source-of-truth files, compatibility statements, change-note requirements, and non-regression expectations. |

# 1. Purpose [SEC:UDQ-SCM-STD-001::1]

This standard defines how UniversalDAQ code, packages, release identifiers, and revision lineage shall be controlled. Its purpose is to ensure that any package sent out for review, test, or release can be unambiguously identified, traced back to a known baseline, and assessed for compatibility and non-regression.

# 2. Scope [SEC:UDQ-SCM-STD-001::2]

This standard applies to:

- Python source code and support scripts
- controlled documentation packaged with code
- send-out zip packages and unpacked review packages
- package-root audit tools
- manifests, release notes, and change summaries
- baseline identifiers used in internal review or external delivery

This standard does not replace Git or another source control tool. It defines the project-facing identification and packaging scheme that shall remain visible even when the underlying repository tooling changes.

# 3. Governing Principles [SEC:UDQ-SCM-STD-001::3]

UniversalDAQ software and package control shall follow these principles:

1. every deliverable package shall have a stable package release ID
2. every package shall identify the code baseline it represents
3. every package shall declare the documentation baseline it carries
4. source-of-truth files shall be explicitly named rather than inferred from memory
5. compatibility claims shall be stated, not assumed
6. changes shall be summarized in human-readable release notes
7. no package shall be treated as authoritative if its manifest and audit position are missing or contradictory
8. send-out packages shall be auditable after unpacking without access to the original authoring environment

# 4. Identifier Families [SEC:UDQ-SCM-STD-001::4]

## 4.1 Code Baseline ID [SEC:UDQ-SCM-STD-001::4.1]

A **Code Baseline ID** shall identify the implementation snapshot represented by a package. The canonical format shall be:

`UDQ-CODE-<program_or_scope>-<major>.<minor>.<patch>-<qualifier>`

Examples:

- `UDQ-CODE-core-0.4.0-WIP`
- `UDQ-CODE-labjack_genesys-11.16.0-RC1`
- `UDQ-CODE-universaldaq-0.1.0-BASELINE`

A code baseline ID shall be unique within the project's documented release history.

## 4.2 Documentation Baseline ID [SEC:UDQ-SCM-STD-001::4.2]

A **Documentation Baseline ID** shall identify the controlled document baseline carried with or associated to a package. The canonical format shall be:

`UDQ-DOC-BASELINE-<YYYYMMDD>-<serial>`

Example:

- `UDQ-DOC-BASELINE-20260321-01`

The documentation baseline shall point to a defined controlled index revision and machine-readable registry set.

## 4.3 Package Release ID [SEC:UDQ-SCM-STD-001::4.3]

A **Package Release ID** shall identify the exact send-out package. The canonical format shall be:

`UDQ-PKG-<scope>-<YYYYMMDD>-<serial>-<state>`

Examples:

- `UDQ-PKG-precode-20260321-01-WIP`
- `UDQ-PKG-review-20260321-02-RC`
- `UDQ-PKG-implementation-20260322-01-REL`

Each sent zip or unpacked delivery package shall have exactly one package release ID.

## 4.4 Manifest ID and Audit Run ID [SEC:UDQ-SCM-STD-001::4.4]

Where a package includes a manifest and audit report, those artifacts shall identify:

- the package release ID
- the code baseline ID
- the documentation baseline ID
- the audit run timestamp
- the auditor version used

# 5. Revision Lineage [SEC:UDQ-SCM-STD-001::5]

## 5.1 Lineage Requirements [SEC:UDQ-SCM-STD-001::5.1]

Package lineage shall remain reconstructable from the package contents alone. At minimum, every package shall state:

- what package it is
- what baseline it supersedes or continues from, if applicable
- what changed since the prior package
- whether the package is WIP, review, release-candidate, or released

## 5.2 Status Labels [SEC:UDQ-SCM-STD-001::5.2]

Permitted top-level package status labels are:

- `WIP`
- `REVIEW`
- `RC`
- `REL`
- `SUPERSEDED`
- `OBSOLETE`

A package shall not simultaneously claim more than one active status.

# 6. Source-of-Truth Files [SEC:UDQ-SCM-STD-001::6]

## 6.1 Source-of-Truth Declaration [SEC:UDQ-SCM-STD-001::6.1]

Every deliverable package shall declare its source-of-truth files. These shall identify, as applicable:

- main application entry point
- backend authority modules
- frontend shell module
- configuration or schema source files
- controlled document index
- active document registry
- requirement registry
- package manifest
- release notes/update summary
- package-root audit tool

## 6.2 Truth Hierarchy [SEC:UDQ-SCM-STD-001::6.2]

The package truth hierarchy shall be:

1. manifest and package release identification
2. package-root audit result and governed package-audit criteria
3. controlled document index and registries
4. declared source-of-truth code files
5. supporting files and exports

If files at lower levels contradict higher-level controlled declarations, the contradiction shall be treated as an audit finding.

# 7. Compatibility Statements [SEC:UDQ-SCM-STD-001::7]

Every package shall carry explicit compatibility statements covering, as relevant:

- expected operating system/runtime
- Python version family
- required external libraries or drivers
- expected device/protocol scope
- compatibility with prior package data or configuration profiles
- known incompatible changes
- migration notes where structure or naming changed

A package shall not imply backward compatibility merely because filenames look similar.

# 8. Change-Note Requirements [SEC:UDQ-SCM-STD-001::8]

Each send-out package shall include a human-readable change note or release note stating:

- package release ID
- previous baseline or comparison point
- headline changes
- added capabilities
- changed behavior
- removed or deprecated behavior
- known issues
- audit status summary
- reviewer/operator attention items

A package that materially changes outputs, authority, restore behavior, sequencing, historian behavior, or remote control posture shall call that out explicitly.

# 9. Non-Regression Expectations [SEC:UDQ-SCM-STD-001::9]

## 9.1 General Rule [SEC:UDQ-SCM-STD-001::9.1]

UniversalDAQ packages shall be developed and reviewed under a non-regression expectation. This means that:

- previously claimed capabilities shall not disappear silently
- changes to existing behavior shall be declared
- compatibility impacts shall be declared
- package notes shall indicate whether the package is intended to preserve, extend, or intentionally replace prior behavior

## 9.2 Evidence Expectations [SEC:UDQ-SCM-STD-001::9.2]

Non-regression claims shall be supported by one or more of:

- package audit results
- review checklist outcomes
- proof-bundle references
- smoke-test or runtime results
- explicit migration notes where behavior is intentionally changed

# 10. Package-Root Auditor Position [SEC:UDQ-SCM-STD-001::10]

The package-root documentation auditor shall be included at the package root for governed send-out packages unless explicitly exempted by the release manifest. The auditor shall serve as the immediate package truth-check for:

- package structure
- required governed documents/artifacts
- dependency and registry integrity
- manifest visibility
- document/control consistency

The auditor shall not replace engineering judgment, but a package lacking a coherent auditor result shall not be treated as baseline-clean.

# 11. Minimum Baseline Artifacts [SEC:UDQ-SCM-STD-001::11]

A governed send-out package shall contain, at minimum:

- package-root auditor
- release manifest
- release notes/update summary
- controlled document index where documents are included
- current machine-readable registries where documents are included
- declared source-of-truth file list
- implementation/audit position appropriate to package class

# 12. Anti-Patterns [SEC:UDQ-SCM-STD-001::12]

The following are prohibited:

- package files with no package release ID
- undocumented baseline drift
- implied compatibility with no compatibility statement
- sending packages that depend on unwritten local knowledge
- conflicting entry points with no source-of-truth declaration
- silent removal of previously relied-upon capabilities
- contradictory manifest, release notes, and audit outputs

# 13. Downstream Obligations [SEC:UDQ-SCM-STD-001::13]

This standard shall govern:

- `UDQ-REL-SPEC-001`
- `UDQ-REL-TPL-001`
- `UDQ-REL-TPL-002`
- package-root audit expectations in `UDQ-AUD-SPEC-001`
- future implementation package baselines and send-out workflows
