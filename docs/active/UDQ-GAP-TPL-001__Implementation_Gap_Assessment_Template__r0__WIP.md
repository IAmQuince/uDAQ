---
document_id: UDQ-GAP-TPL-001
title: Implementation Gap Assessment Template
revision: r0
status: WIP
classification:
  domain: GAP
  type: TPL
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-GAP-RPT-001
- UDQ-QUAL-SPEC-002
- UDQ-GOV-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
audit_exceptions: []
---
# Implementation Gap Assessment Template

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-21 | WIP | Initial issue providing the governed form for recording, prioritizing, and closing implementation gaps against the UniversalDAQ controlled baseline. |

# 1. Purpose [SEC:UDQ-GAP-TPL-001::1]

This template defines the minimum governed structure for a UniversalDAQ implementation gap record. It converts the open-gap concept into a reusable operating form that can be linked to requirements, specifications, baselines, proof bundles, and closure decisions.

# 2. Usage Rules [SEC:UDQ-GAP-TPL-001::2]

A gap assessment shall be created when any of the following are true:

- a required capability is not yet implemented,
- an implemented capability lacks governed proof,
- a package claims scope that its artifacts do not yet satisfy,
- a subsystem has known behavioral limitations that materially affect review or release posture,
- an audit, review, or runtime observation identifies a bounded defect or incompleteness.

A gap record shall not be a vague note. It shall identify a bounded issue, its affected requirements or specs, its current state, its target closure condition, and the evidence expected when it is closed.

# 3. Recommended Filename [SEC:UDQ-GAP-TPL-001::3]

Recommended filename pattern:

`UDQ_GAP_<GAP-ID>.md`

Example:

`UDQ_GAP_GAP-UI-001.md`

# 4. Required Field Set [SEC:UDQ-GAP-TPL-001::4]

Every implementation gap assessment shall include, at minimum:

- gap ID,
- title,
- status,
- priority or severity,
- affected baseline or package ID,
- linked requirement IDs where applicable,
- linked document IDs and section IDs,
- current state,
- target state,
- impact,
- dependencies or blockers,
- closure criteria,
- expected proof when closed,
- owner or responsible reviewer,
- revision history.

# 5. Machine-Readable Core Fields [SEC:UDQ-GAP-TPL-001::5]

The following fields are the machine-readable core and should remain stable even if display formatting changes later:

- `gap_id`
- `title`
- `status`
- `priority`
- `affected_baseline`
- `linked_requirements`
- `linked_documents`
- `linked_sections`
- `current_state`
- `target_state`
- `impact`
- `dependencies`
- `blockers`
- `closure_criteria`
- `expected_proof`
- `owner`
- `disposition`
- `notes`

# 6. Template [SEC:UDQ-GAP-TPL-001::6]

```markdown
# UniversalDAQ Implementation Gap Assessment

## Identity
- Gap ID: `GAP-XXX-001`
- Title:
- Status: `OPEN | TRIAGED | IN_PROGRESS | BLOCKED | READY_FOR_REVIEW | CLOSED`
- Priority: `CRITICAL | HIGH | MEDIUM | LOW`
- Affected Baseline / Package ID:
- Owner:
- Date Opened:
- Last Updated:

## Linked References
- Requirement IDs:
- Document IDs:
- Section IDs:
- Related audit findings:
- Related proof bundle IDs:
- Related package IDs:

## Current State
Describe the system as it exists today, including what is missing, incorrect, unproven, or unstable.

## Target State
Describe the expected state once the gap is closed.

## Impact
- User / operator impact:
- Architecture / subsystem impact:
- Package / release impact:
- Safety / authority / truthfulness impact:
- Review / audit impact:

## Dependencies and Blockers
- Dependencies:
- Active blockers:
- Upstream assumptions:

## Proposed Closure Criteria
- Criterion 1
- Criterion 2
- Criterion 3

## Expected Proof at Closure
- Required proof artifacts:
- Required runtime evidence:
- Required screenshots / exports / logs:
- Required reviewer checks:

## History / Notes
- YYYY-MM-DD:
- YYYY-MM-DD:
```

# 7. Completion Rules [SEC:UDQ-GAP-TPL-001::7]

A gap record is not complete unless:

- the issue is bounded enough to act on,
- affected controlled references are named,
- closure criteria are testable or reviewable,
- expected proof is stated,
- the record is updated when status changes.

A gap shall not be marked `CLOSED` unless the linked closure proof exists and the closure reasoning is recorded.

# 8. Relationship to Other Governed Artifacts [SEC:UDQ-GAP-TPL-001::8]

This template should be used together with:

- `UDQ-GAP-RPT-001` for aggregated open-gap reporting,
- `UDQ-QUAL-SPEC-002` for determining what counts as adequate closure proof,
- package audit reports when gaps are discovered during packaging or review,
- release notes when a package intentionally carries unresolved gaps.

# 9. Anti-Patterns [SEC:UDQ-GAP-TPL-001::9]

The following are prohibited:

- gap records with no linked scope or references,
- "needs work" style summaries with no bounded target state,
- marking a gap closed because work feels mostly done,
- recording only symptoms and not the expected closure condition,
- using one gap record to hide multiple unrelated problems.
