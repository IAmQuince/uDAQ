---
document_id: UDQ-AUD-TPL-001
title: Package Audit Report Template
revision: r0
status: WIP
classification:
  domain: AUD
  type: TPL
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-AUD-SPEC-001
- UDQ-REL-SPEC-001
- UDQ-SCM-STD-001
- UDQ-GOV-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
audit_exceptions: []
---
# Package Audit Report Template

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-21 | WIP | Initial issue providing the governed human-readable package audit report form aligned to the package audit specification and send-out package model. |

# 1. Purpose [SEC:UDQ-AUD-TPL-001::1]

This template defines the minimum governed report structure for a UniversalDAQ package audit. It is the human-readable companion to the machine-readable audit outputs emitted by the package-root auditor.

# 2. Usage Rules [SEC:UDQ-AUD-TPL-001::2]

A package audit report should be generated or completed whenever:

- a review package is prepared for circulation,
- a release-candidate package is proposed,
- a package fails audit and needs a triage record,
- a package passes with accepted exceptions or bounded warnings,
- a reviewer wants a preserved narrative audit record in addition to JSON or CSV outputs.

The report shall identify what package was checked, by which tool/profile, what was found, and what disposition followed.

# 3. Recommended Filename [SEC:UDQ-AUD-TPL-001::3]

Recommended filename pattern:

`UDQ_PACKAGE_AUDIT__<TIMESTAMP>.md`

# 4. Required Field Set [SEC:UDQ-AUD-TPL-001::4]

Every package audit report shall include, at minimum:

- package release ID,
- audited package path or artifact identity,
- audit timestamp,
- auditor filename and version,
- audit profile,
- overall result,
- failure/warning counts,
- key findings,
- artifact inventory summary,
- disposition,
- reviewer notes.

# 5. Machine-Readable Core Fields [SEC:UDQ-AUD-TPL-001::5]

The following fields are the machine-readable core and should remain stable even if the display form changes later:

- `package_release_id`
- `audit_timestamp`
- `auditor_file`
- `auditor_version`
- `audit_profile`
- `overall_result`
- `failure_count`
- `warning_count`
- `info_count`
- `finding_codes`
- `disposition`
- `reviewer`

# 6. Template [SEC:UDQ-AUD-TPL-001::6]

```markdown
# UniversalDAQ Package Audit Report

## Identity
- Package Release ID:
- Package Class:
- Package Status:
- Audited Artifact / Path:
- Audit Timestamp:
- Auditor File:
- Auditor Version:
- Audit Profile:
- Reviewer:

## Summary Result
- Overall Result: `PASS | PASS_WITH_WARNINGS | FAIL`
- Failure Count:
- Warning Count:
- Info Count:
- Disposition: `ACCEPTED | ACCEPTED_WITH_EXCEPTIONS | REJECTED | INTERNAL_WIP_ONLY`

## Findings Summary
### Failures
- Finding code:
- Affected artifact:
- Summary:
- Expected correction:

### Warnings
- Finding code:
- Affected artifact:
- Summary:
- Rationale if accepted:

### Informational Items
- Finding code:
- Summary:

## Artifact Inventory Summary
- Controlled document count:
- Registry artifact count:
- Required root files present:
- Missing required files:
- Non-empty file checks:
- Dependency resolution summary:

## Reviewer Notes
- Item 1
- Item 2

## Follow-Up Actions
- Action 1
- Action 2

## Linked Artifacts
- JSON audit output:
- CSV findings output:
- Manifest:
- Release notes:
- Related gap or proof bundles:
```

# 7. Completion Rules [SEC:UDQ-AUD-TPL-001::7]

A package audit report is not complete unless:

- it identifies the exact package audited,
- the tool/profile used are explicit,
- the result and disposition are both stated,
- significant failures or accepted warnings are summarized,
- linked machine-readable outputs are named where they exist.

# 8. Relationship to Other Governed Artifacts [SEC:UDQ-AUD-TPL-001::8]

This template should be used together with:

- `UDQ-AUD-SPEC-001` for result semantics,
- release manifests and release notes for package identity and scope,
- the package-root auditor JSON and CSV outputs,
- gap or proof records when findings are carried into follow-up work.

# 9. Anti-Patterns [SEC:UDQ-AUD-TPL-001::9]

The following are prohibited:

- audit reports that do not identify the package audited,
- using only "pass/fail" with no finding context,
- accepting warnings without recording why they are acceptable,
- listing linked artifacts that are not actually present,
- recording a favorable disposition that contradicts the audit result without explanation.
