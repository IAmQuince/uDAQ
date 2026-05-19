---
document_id: UDQ-PROOF-TPL-001
title: Implementation Proof Bundle Template
revision: r0
status: WIP
classification:
  domain: PROOF
  type: TPL
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-QUAL-SPEC-002
- UDQ-REQ-MAT-001
- UDQ-SCM-STD-001
- UDQ-GOV-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
audit_exceptions: []
---
# Implementation Proof Bundle Template

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-21 | WIP | Initial issue providing the governed bundle form for showing that a UniversalDAQ capability is implemented, exercised, and reviewable against controlled requirements. |

# 1. Purpose [SEC:UDQ-PROOF-TPL-001::1]

This template defines the minimum governed structure for an implementation proof bundle. A proof bundle is the review package that ties implemented behavior to requirements, baselines, evidence artifacts, and a bounded conclusion.

# 2. Usage Rules [SEC:UDQ-PROOF-TPL-001::2]

A proof bundle should be assembled when any of the following are true:

- a subsystem reaches a claimed completion milestone,
- a package claims implementation of new or revised requirements,
- a gap is being closed,
- a reviewer needs evidence that a behavior is real rather than planned,
- a release or integration decision depends on implementation evidence.

A proof bundle may cover one requirement, one subsystem, or a bounded cluster of tightly related requirements, but the scope shall be explicit.

# 3. Recommended Filename [SEC:UDQ-PROOF-TPL-001::3]

Recommended filename pattern:

`UDQ_PROOF_<BUNDLE-ID>.md`

Example:

`UDQ_PROOF_PROOF-OUT-001.md`

# 4. Required Field Set [SEC:UDQ-PROOF-TPL-001::4]

Every implementation proof bundle shall include, at minimum:

- proof bundle ID,
- title,
- covered requirement IDs,
- covered subsystem(s),
- code/package baseline IDs,
- implementation scope statement,
- evidence inventory,
- test or runtime execution context,
- observations,
- known limitations,
- reviewer conclusion,
- revision history.

# 5. Machine-Readable Core Fields [SEC:UDQ-PROOF-TPL-001::5]

The following fields are the machine-readable core and should remain stable even if the surrounding report format evolves:

- `proof_bundle_id`
- `title`
- `covered_requirements`
- `covered_subsystems`
- `code_baseline_id`
- `package_release_id`
- `documentation_baseline_id`
- `scope_statement`
- `evidence_inventory`
- `execution_context`
- `observations`
- `known_limitations`
- `conclusion`
- `reviewers`

# 6. Template [SEC:UDQ-PROOF-TPL-001::6]

```markdown
# UniversalDAQ Implementation Proof Bundle

## Identity
- Proof Bundle ID: `PROOF-XXX-001`
- Title:
- Status: `DRAFT | UNDER_REVIEW | ACCEPTED | PARTIALLY_ACCEPTED | REJECTED`
- Issue Date:
- Last Updated:
- Author / Assembler:
- Reviewers:

## Covered Scope
- Requirement IDs:
- Document IDs / Section IDs:
- Covered subsystem(s):
- Gap IDs closed or addressed:
- Package Release ID:
- Code Baseline ID:
- Documentation Baseline ID:

## Scope Statement
Describe exactly what this proof bundle claims to prove and what it does not claim to prove.

## Evidence Inventory
- Test records:
- Runtime logs:
- Screenshots:
- Exports / bundles:
- Audit outputs:
- Supporting files:
- Reviewer notes:

## Execution Context
- Environment:
- Profile / mode:
- Devices or simulators used:
- Inputs / scenarios exercised:
- Runtime assumptions:
- Known deviations from target deployment:

## Observations
- Observation 1
- Observation 2
- Observation 3

## Requirement-to-Evidence Mapping
| Requirement ID | Evidence Item | Observation Summary | Disposition |
|---|---|---|---|
| UDQ-REQ-XXX | Evidence reference | Summary | `PROVEN | PARTIALLY_PROVEN | NOT_PROVEN` |

## Known Limitations
- Item 1
- Item 2

## Reviewer Conclusion
- Overall conclusion:
- Requirements proven:
- Requirements partially proven:
- Requirements not yet proven:
- Follow-up actions:
- Approval / disposition:

## Revision History
- YYYY-MM-DD:
- YYYY-MM-DD:
```

# 7. Completion Rules [SEC:UDQ-PROOF-TPL-001::7]

A proof bundle is not complete unless:

- the scope being proven is explicitly bounded,
- requirements are named rather than implied,
- evidence items are identifiable and reviewable,
- observations are stated in relation to real evidence,
- the conclusion distinguishes proven, partially proven, and unproven aspects.

# 8. Relationship to Other Governed Artifacts [SEC:UDQ-PROOF-TPL-001::8]

This template should be used together with:

- `UDQ-QUAL-SPEC-002` to determine adequacy of evidence,
- `UDQ-REQ-MAT-001` to map proof back to requirements,
- gap assessments when a proof bundle closes an implementation gap,
- release/package governance docs when the proof supports a baseline or send-out package.

# 9. Anti-Patterns [SEC:UDQ-PROOF-TPL-001::9]

The following are prohibited:

- proof bundles that contain conclusions without evidence,
- screenshots with no linked requirement or scope statement,
- claiming "works" without execution context,
- using a proof bundle to hide known failures or limitations,
- equating existence of code with proven behavior.
