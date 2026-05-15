---
document_id: UDQ-REL-TPL-002
title: Release Notes and Update Summary Template
revision: r0
status: WIP
classification:
  domain: REL
  type: TPL
  sequence: '002'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-REL-SPEC-001
- UDQ-SCM-STD-001
- UDQ-QUAL-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Release Notes and Update Summary Template

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-21 | WIP | Initial issue providing the minimum release-note and update-summary structure for UniversalDAQ send-out packages. |

# 1. Purpose [SEC:UDQ-REL-TPL-002::1]

This template defines the minimum human-readable update summary that shall accompany a governed UniversalDAQ send-out package.

# 2. Recommended Filename [SEC:UDQ-REL-TPL-002::2]

Recommended release-notes filename:

`docs/release/RELEASE_NOTES.md`

# 3. Template [SEC:UDQ-REL-TPL-002::3]

```markdown
# UniversalDAQ Release Notes

## Package Identity
- Package Release ID: `UDQ-PKG-precode-20260321-01-WIP`
- Package Class: `PRECODE_BASELINE`
- Package Status: `WIP`
- Issue Date: `2026-03-21`
- Code Baseline ID: `NO_CODE_SCOPE`
- Documentation Baseline ID: `UDQ-DOC-BASELINE-20260321-01`
- Comparison Baseline: `N/A`

## Summary
Provide a concise summary of what this package is for and how it should be used.

## Added
- Item 1
- Item 2

## Changed
- Item 1
- Item 2

## Removed / Deprecated
- Item 1
- Item 2

## Compatibility
- Python / runtime expectations:
- Device / protocol scope:
- Backward-compatibility statement:
- Known incompatible changes:

## Source of Truth
- Manifest:
- Auditor:
- Main entry points:
- Controlled index / registry artifacts:

## Audit Status
- Auditor profile used:
- Auditor outcome:
- Known warnings:
- Known failures accepted by exception:

## Reviewer Attention Items
- Item 1
- Item 2

## Known Issues / Limitations
- Item 1
- Item 2

## Next Expected Moves
- Item 1
- Item 2
```

# 4. Required Content Rules [SEC:UDQ-REL-TPL-002::4]

Release notes shall not be treated as optional commentary. They shall state:

- what changed
- what stayed intentionally stable
- what reviewers should pay attention to
- what compatibility assumptions are being made
- what audit posture the package currently has

# 5. Special Callout Rules [SEC:UDQ-REL-TPL-002::5]

The release notes shall explicitly call out any changes affecting:

- output authority/arbitration
- restore/autosave/profile behavior
- sequencing behavior
- historian/event/evidence behavior
- device/protocol support
- remote supervision/control posture
- package structure or truth-source files

# 6. Anti-Patterns [SEC:UDQ-REL-TPL-002::6]

The following are prohibited:

- release notes that say only "misc fixes"
- no comparison point for a materially changed package
- claiming backward compatibility while also listing undeclared breaking changes
- omitting known issues that a reviewer is likely to encounter
