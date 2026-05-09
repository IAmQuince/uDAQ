---
document_id: UDQ-AUD-CHK-001
title: Local VSCode Review Checklist
revision: r2
status: WIP
document_class: checklist
classification:
  domain: AUD
  type: CHK
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-AUD-SPEC-001
- UDQ-AUD-SPEC-002
- UDQ-GOV-LOG-001
- UDQ-QUAL-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Local VSCode Review Checklist

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r2 | 2026-03-21 | WIP | Renames drafting-review language to reduce scan noise and aligns the checklist to the allowed-pattern model. |
| r1 | 2026-03-21 | WIP | Removes scan-noise wording and clarifies governed form-field review. |
| r0 | 2026-03-21 | WIP | Initial practical pre-package review checklist for local engineering use. |

# 1. Purpose [SEC:UDQ-AUD-CHK-001::1]

This checklist provides a practical local review flow before packaging or sending a UniversalDAQ working set. It complements the package-root auditor and does not replace governed audit results.

# 2. Usage Position [SEC:UDQ-AUD-CHK-001::2]

This checklist is intended for use in a local editor workflow such as VSCode when an engineer wants to review the package before running or after running the package-root auditor.

# 3. Checklist [SEC:UDQ-AUD-CHK-001::3]

## 3.1 Package Root Sanity [SEC:UDQ-AUD-CHK-001::3.1]

- [ ] Open the intended package root and confirm you are reviewing the correct folder.
- [ ] Confirm the package-root auditor file is present at the top level.
- [ ] Confirm `audit_reports/` exists or will be created by the auditor.
- [ ] Confirm there are no obviously misplaced controlled files.

## 3.2 Controlled Document Review [SEC:UDQ-AUD-CHK-001::3.2]

- [ ] Confirm active controlled docs follow the controlled filename convention.
- [ ] Spot-check YAML front matter on revised/new docs.
- [ ] Confirm revision and status in filename and YAML match.
- [ ] Confirm new docs have revision history.
- [ ] Confirm normative sections carry stable section IDs.
- [ ] Confirm newly added docs are listed in the controlled index and registry set.

## 3.3 Draft-Residue and Drift Review [SEC:UDQ-AUD-CHK-001::3.3]

- [ ] Search for unfinished drafting residue, unresolved template markers, and similar editorial remnants.
- [ ] Confirm any remaining governed form fields are intentional, class-appropriate, and explicitly bounded.
- [ ] Search for stale filenames, outdated revision references, or superseded document names.
- [ ] Confirm copied text has been properly adapted rather than left generic.

## 3.4 Dependency and Cross-Reference Review [SEC:UDQ-AUD-CHK-001::3.4]

- [ ] Open the controlled index and verify the active set matches the intended send-out baseline.
- [ ] Confirm newly referenced dependencies exist and are not empty.
- [ ] Confirm machine-readable artifacts point to existing files.
- [ ] Spot-check that major `depends_on` references make sense.
- [ ] Spot-check that referenced requirement IDs or section IDs exist where used.

## 3.5 Substantive Review [SEC:UDQ-AUD-CHK-001::3.5]

- [ ] Confirm the package does not merely contain document shells.
- [ ] Confirm new docs are written at the correct layer of abstraction.
- [ ] Confirm no document silently contradicts the foundation narratives.
- [ ] Confirm no package notes claim completion beyond what the proof model would allow.

## 3.6 Audit Run [SEC:UDQ-AUD-CHK-001::3.6]

- [ ] Run the package-root auditor using the appropriate profile.
- [ ] Read the console output rather than relying only on exit status.
- [ ] Open the generated Markdown report.
- [ ] Review FAIL and WARN items one by one.
- [ ] Re-run the auditor after correcting issues.

## 3.7 Pre-Send Gate [SEC:UDQ-AUD-CHK-001::3.7]

- [ ] Confirm the package contains the artifacts the recipient is expected to review.
- [ ] Confirm audit artifacts reflect the current package state rather than an old run.
- [ ] Confirm any known limitations are documented honestly.
- [ ] Confirm the package is small/tidy enough that a reviewer can navigate it without guesswork.

# 4. Expected Deliverables Before Sending [SEC:UDQ-AUD-CHK-001::4]

For meaningful send-out packages, the reviewer should normally expect:

- controlled documents
- machine-readable registries
- package-root auditor
- audit report outputs
- any release/readme notes required by the package class

# 5. Relationship to Proof Model [SEC:UDQ-AUD-CHK-001::5]

Completion of this checklist is review support, not proof by itself. Runtime or behavioral claims still require evidence governed by `UDQ-QUAL-SPEC-002`.

# 6. Immediate Application [SEC:UDQ-AUD-CHK-001::6]

This checklist should be used whenever the UniversalDAQ controlled corpus is packaged for review, especially after multi-document revision sprints or package-structure changes.
