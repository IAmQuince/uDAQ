---
document_id: UDQ-GOV-STD-001
title: Document Control Scheme
revision: r3
status: WIP
classification:
  domain: GOV
  type: STD
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on: []
supersedes: []
superseded_by: []
machine_readable_artifacts: []
audit_exceptions:
- DOC-PLACE-001
---
# Document Control Scheme

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r3 | 2026-03-21 | WIP | Corrected stale document-ID examples, removed unresolved reviewer placeholders, and aligned the scheme to the current governed document family. |
| r2 | 2026-03-21 | WIP | Retrofitted to YAML front matter, stable section IDs, and the machine-readable cross-reference scheme. |
| r1 | 2026-03-21 | WIP | First controlled revision created by placing the document under the universalDAQ document control scheme and establishing formal metadata and revision history. |

## 1. Purpose [SEC:UDQ-GOV-STD-001::1]

This scheme defines how all project documents are identified, versioned, reviewed, approved, revised, archived, and referenced across the universalDAQ project. It is intended to be robust enough to cover early concept notes, working engineering drafts, design narratives, requirements, matrices, procedures, test protocols, test records, software package notes, release artifacts, meeting records, issue logs, and future manufacturing or field documents.

The goals are:
- one unambiguous identity for every document
- clear distinction between draft, working, released, superseded, and obsolete material
- traceable revision history
- consistent cross-referencing between documents, code, tests, and release packages
- controlled growth as the project moves from concept through implementation and maintenance

---

## 2. Governing Principles [SEC:UDQ-GOV-STD-001::2]

1. **Every controlled document has a unique document ID.** File names alone are not sufficient.
2. **Every controlled document has a revision identifier and status.**
3. **Released documents are immutable.** Changes require a new revision.
4. **Drafts may evolve rapidly, but must still retain revision history.**
5. **Superseded documents remain archived and retrievable.** They are never silently overwritten.
6. **Cross-document references should point to document ID + revision where practical.**
7. **A package release should identify the exact document revisions included.**
8. **Templates are controlled documents too.**
9. **Generated reports are records, not templates.**
10. **Working notes may exist outside strict control briefly, but once they influence requirements, architecture, testing, release, or acceptance, they should be brought under control.**

---

## 3. Document Classes [SEC:UDQ-GOV-STD-001::3]

The scheme should support at least the following classes.

### 3.1 Governance / Definition Documents [SEC:UDQ-GOV-STD-001::3.1]
Used to define how the project is run.
- project charter
- document control plan
- coding standards
- review checklists
- package audit specs
- anti-pattern policies

### 3.2 Architecture / Design Documents [SEC:UDQ-GOV-STD-001::3.2]
Used to define what the system is and how it works.
- system controls narrative
- platform controls narrative
- subsystem design docs
- interface control documents
- data model specs
- state machine definitions
- communication architecture docs

### 3.3 Requirements Documents [SEC:UDQ-GOV-STD-001::3.3]
Used to define what must be true.
- requirements specifications
- requirements traceability matrix
- subsystem completion criteria
- acceptance criteria docs

### 3.4 Implementation / Build Documents [SEC:UDQ-GOV-STD-001::3.4]
Used to guide construction.
- implementation plans
- module dependency maps
- package manifests
- build/run instructions
- deployment instructions

### 3.5 Verification / Validation Documents [SEC:UDQ-GOV-STD-001::3.5]
Used to prove correctness.
- test plans
- test procedures
- test protocols
- test reports
- diagnostic harness definitions
- verification evidence matrices

### 3.6 Operational Documents [SEC:UDQ-GOV-STD-001::3.6]
Used during execution or field use.
- startup procedures
- shutdown procedures
- recovery procedures
- operator guides
- troubleshooting guides
- maintenance procedures

### 3.7 Project Records [SEC:UDQ-GOV-STD-001::3.7]
Used to preserve history and evidence.
- meeting minutes
- decision logs
- change logs
- issue logs
- review records
- release notes
- audit reports
- captured diagnostics

### 3.8 Templates / Forms [SEC:UDQ-GOV-STD-001::3.8]
Reusable controlled skeletons.
- report templates
- review forms
- test record forms
- release checklist templates

### 3.9 External Reference Registers [SEC:UDQ-GOV-STD-001::3.9]
Used to control outside dependencies.
- standards register
- vendor reference register
- external library register
- cited paper/patent/reference list

---

## 4. Document States [SEC:UDQ-GOV-STD-001::4]

Every controlled document should have one of these statuses.

### 4.1 WIP [SEC:UDQ-GOV-STD-001::4.1]
Working draft. Under active development. Not authoritative.

### 4.2 REVIEW [SEC:UDQ-GOV-STD-001::4.2]
Under formal review. Changes should be limited and tracked.

### 4.3 APPROVED [SEC:UDQ-GOV-STD-001::4.3]
Approved for project use, but not necessarily tied to a released package.

### 4.4 RELEASED [SEC:UDQ-GOV-STD-001::4.4]
Frozen and authoritative for a specific package, milestone, or baseline.

### 4.5 SUPERSEDED [SEC:UDQ-GOV-STD-001::4.5]
Replaced by a newer revision. Kept for traceability.

### 4.6 OBSOLETE [SEC:UDQ-GOV-STD-001::4.6]
No longer applicable to the project. Kept only for historical record.

### 4.7 RECORD [SEC:UDQ-GOV-STD-001::4.7]
Evidence document created from execution of work. Not revised in the same way as design docs; corrections should append rather than overwrite where possible.

---

## 5. Revision Scheme [SEC:UDQ-GOV-STD-001::5]

Use a two-track revision model.

### 5.1 Draft Revision [SEC:UDQ-GOV-STD-001::5.1]
For active drafting:
- `r0`, `r1`, `r2`, ...

Example:
- `UDQ-ARCH-SYS-001_r3`

This is good for rapid internal iteration.

### 5.2 Released Revision [SEC:UDQ-GOV-STD-001::5.2]
For approved/released baselines:
- `Rev A`, `Rev B`, `Rev C`, ...
- optionally paired with package tag if needed

Example:
- `UDQ-ARCH-SYS-001_RevA`

### 5.3 Minor Editorial Marker (optional) [SEC:UDQ-GOV-STD-001::5.3]
If needed for non-technical edits that do not change meaning:
- `Rev A.1`, `Rev A.2`

Only use this if the team is disciplined about what counts as editorial.
If there is any doubt, increment the full revision.

### 5.4 Rule [SEC:UDQ-GOV-STD-001::5.4]
Do not mix multiple incompatible schemes across the same project.
Use `r#` while drafting and switch to `RevX` at formal release.

---

## 6. Document ID Scheme [SEC:UDQ-GOV-STD-001::6]

Each controlled document gets a persistent ID in this format:

`UDQ-[DOMAIN]-[TYPE]-[NNN]`

Where:
- `UDQ` = universalDAQ project prefix
- `DOMAIN` = major project domain
- `TYPE` = document type code
- `NNN` = sequential number within that domain/type

### 6.1 Domain Codes [SEC:UDQ-GOV-STD-001::6.1]
Suggested starting set:
- `GOV` = governance
- `ARCH` = architecture
- `REQ` = requirements
- `IMPL` = implementation
- `VER` = verification / validation
- `OPS` = operations
- `REL` = release / packaging
- `PM` = project management / records
- `TPL` = templates
- `EXT` = external references
- `SW` = software-specific detailed docs
- `HW` = hardware-specific detailed docs
- `INTF` = interfaces / ICDs
- `DATA` = data schemas / historian / signal models

### 6.2 Type Codes [SEC:UDQ-GOV-STD-001::6.2]
Suggested starting set:
- `NAR` = narrative
- `SPEC` = specification
- `MAT` = matrix
- `PLAN` = plan
- `PROC` = procedure
- `WKI` = work instruction
- `RPT` = report
- `LOG` = log/register
- `CHK` = checklist
- `TPL` = template
- `FORM` = form
- `MAP` = dependency map
- `ICD` = interface control document
- `STD` = standard
- `GUIDE` = guide

### 6.3 Examples [SEC:UDQ-GOV-STD-001::6.3]
- `UDQ-ARCH-NAR-001` = System Controls Narrative
- `UDQ-ARCH-NAR-002` = Platform Controls Narrative
- `UDQ-REQ-MAT-001` = Requirements Traceability Matrix
- `UDQ-REQ-SPEC-001` = Definition of Complete by Subsystem
- `UDQ-REL-SPEC-001` = Package Audit Spec
- `UDQ-GOV-STD-001` = Document Control Scheme
- `UDQ-VER-PLAN-001` = Verification Master Plan
- `UDQ-VER-RPT-004` = Weekend Run Test Report 4
- `UDQ-PM-LOG-001` = Decision Log
- `UDQ-TPL-TPL-001` = Package Audit Report Template

### 6.4 Important Rule [SEC:UDQ-GOV-STD-001::6.4]
The document ID should not change when the document title changes slightly.
The ID is permanent.

---

## 7. File Naming Convention [SEC:UDQ-GOV-STD-001::7]

Use a file naming format that is human-readable but also machine-sortable:

`[DocID]__[ShortTitle]__[Revision]__[Status].[ext]`

Example:
- `UDQ-ARCH-NAR-001__System_Controls_Narrative__r2__WIP.md`
- `UDQ-ARCH-NAR-001__System_Controls_Narrative__RevA__RELEASED.pdf`
- `UDQ-REQ-MAT-001__Requirements_Traceability_Matrix__r1__REVIEW.xlsx`
- `UDQ-VER-RPT-004__Weekend_Run_Test_Report__RevA__RECORD.pdf`

### 7.1 Filename Rules [SEC:UDQ-GOV-STD-001::7.1]
- use underscores, not spaces
- avoid ambiguous dates in titles
- place dates in metadata, not as the primary identity
- preserve extension by document type
- keep short titles stable once the document matures

---

## 8. Required Document Metadata [SEC:UDQ-GOV-STD-001::8]

Every controlled document should contain a header block near the top with at least:

- Document Title
- Document ID
- Revision
- Status
- Owner
- Reviewer(s)
- Approver (if applicable)
- Effective Date
- Last Updated Date
- Source/Basis Documents
- Supersedes
- Related Documents
- Package/Baseline Association (if any)

### 8.1 Recommended Header Example [SEC:UDQ-GOV-STD-001::8.1]

- **Title:** System Controls Narrative  
- **Document ID:** UDQ-ARCH-NAR-001  
- **Revision:** r2  
- **Status:** REVIEW  
- **Owner:** Scott Fackler  
- **Reviewer(s):** Assigned by current review cycle  
- **Approver:** Assigned by current approval cycle  
- **Effective Date:** 2026-03-21  
- **Last Updated:** 2026-03-21  
- **Supersedes:** UDQ-ARCH-NAR-001 r1  
- **Related Documents:** UDQ-ARCH-NAR-002, UDQ-REQ-MAT-001  
- **Baseline/Package:** Precode Docs Baseline B0  

---

## 9. Revision History Section [SEC:UDQ-GOV-STD-001::9]

Each document should have a revision history table.

Minimum columns:
- Revision
- Date
- Author
- Status
- Summary of Change

Example:

| Revision | Date | Author | Status | Summary of Change |
|---|---|---|---|---|
| r0 | 2026-03-20 | SF | WIP | Initial scaffold |
| r1 | 2026-03-21 | SF | REVIEW | Added control pipeline, authority, safe-state doctrine |
| RevA | 2026-04-02 | SF | RELEASED | First approved project baseline |

Rule: revision notes should say what materially changed, not just “updated.”

---

## 10. Baselines and Package Control [SEC:UDQ-GOV-STD-001::10]

A **baseline** is a frozen set of document revisions considered coherent together.

### 10.1 Baseline Naming [SEC:UDQ-GOV-STD-001::10.1]
Use:
- `B0`, `B1`, `B2`, ... for document baselines
- optionally map to software package releases later

Examples:
- `Precode Baseline B0`
- `Weekend Run Baseline B1`
- `Release Candidate Baseline B2`

### 10.2 Baseline Manifest [SEC:UDQ-GOV-STD-001::10.2]
Every baseline should have a manifest document listing:
- document IDs
- titles
- revisions
- statuses
- included files
- exclusions if relevant

Suggested document:
- `UDQ-REL-LOG-001` = Baseline Manifest / Controlled Document Index

### 10.3 Package Rule [SEC:UDQ-GOV-STD-001::10.3]
Any code/test/package release should cite the exact document baseline it was built against.

---

## 11. Change Control Rules [SEC:UDQ-GOV-STD-001::11]

### 11.1 Minor Changes [SEC:UDQ-GOV-STD-001::11.1]
Typos, formatting, or clarity edits that do not alter technical meaning.
May remain in draft revision track unless already released.

### 11.2 Major Changes [SEC:UDQ-GOV-STD-001::11.2]
Any change affecting:
- requirements
- architecture
- behavior
- interfaces
- safety logic
- test criteria
- release acceptance
- traceability

These require a revision increment and revision note.

### 11.3 Change Initiation Sources [SEC:UDQ-GOV-STD-001::11.3]
A revision may be triggered by:
- design evolution
- code reality diverging from docs
- bug/failure review
- weekend run findings
- new subsystem introduction
- stakeholder review
- packaging audit
- new test evidence

### 11.4 Change Review Requirement [SEC:UDQ-GOV-STD-001::11.4]
Any major architecture, requirements, interface, or verification document should not move to APPROVED/RELEASED without explicit review.

---

## 12. Review and Approval Model [SEC:UDQ-GOV-STD-001::12]

Use proportional rigor.

### 12.1 Solo Working Mode [SEC:UDQ-GOV-STD-001::12.1]
If you are still in rapid development, you may act as author and provisional approver, but the document should still show that explicitly.

### 12.2 Formal Review Mode [SEC:UDQ-GOV-STD-001::12.2]
For high-impact docs, use at least:
- Author
- Technical Reviewer
- Approver

### 12.3 Approval Threshold [SEC:UDQ-GOV-STD-001::12.3]
The following should generally require formal approval before being treated as authoritative:
- requirements docs
- architecture docs
- interface docs
- acceptance criteria docs
- release audit specs
- operational procedures affecting safe state

---

## 13. Controlled vs Uncontrolled Documents [SEC:UDQ-GOV-STD-001::13]

### 13.1 Controlled [SEC:UDQ-GOV-STD-001::13.1]
A document is controlled if it affects:
- what the system must do
- how it is built
- how it is tested
- how it is operated
- whether a release is acceptable

### 13.2 Uncontrolled [SEC:UDQ-GOV-STD-001::13.2]
Examples:
- scratch notes
- personal brainstorming
- throwaway comparisons
- screenshots without formal interpretation

### 13.3 Promotion Rule [SEC:UDQ-GOV-STD-001::13.3]
If uncontrolled material starts influencing project decisions, migrate its content into a controlled document.

---

## 14. Records Management [SEC:UDQ-GOV-STD-001::14]

Records are evidence of something that happened.

Examples:
- test execution reports
- audit reports
- review minutes
- diagnostic logs captured for a run
- release signoff sheets

### 14.1 Record Rules [SEC:UDQ-GOV-STD-001::14.1]
- do not overwrite issued records
- corrections should be appended or reissued as a new record revision with clear explanation
- preserve timestamps and provenance
- bind records to the exact package/baseline where possible

---

## 15. Cross-Reference Rules [SEC:UDQ-GOV-STD-001::15]

When a document references another controlled document, prefer:
- Document ID
- Title
- Revision if the reference is revision-specific

Example:
- “Derived signal quality rules shall conform to UDQ-ARCH-NAR-002 RevA and UDQ-REQ-MAT-001 RevA.”

For flexible draft work, revisionless references are acceptable temporarily, but before release the references should be tightened.

---

## 16. Relationship to Code and Test Artifacts [SEC:UDQ-GOV-STD-001::16]

Documents should be able to point into implementation and evidence.

Recommended fields or appendices:
- related modules/files
- related tests
- related package versions
- related issue IDs
- related diagnostics bundle IDs

This helps prevent documentation from floating free of the actual software.

---

## 17. Master Registers to Maintain [SEC:UDQ-GOV-STD-001::17]

I recommend maintaining these central registers early:

### 17.1 Controlled Document Index [SEC:UDQ-GOV-STD-001::17.1]
Lists every controlled document with current revision and status.
Suggested ID: `UDQ-GOV-LOG-001`

### 17.2 Decision Log [SEC:UDQ-GOV-STD-001::17.2]
Captures significant project decisions and rationale.
Suggested ID: `UDQ-PM-LOG-001`

### 17.3 Open Gaps / Action Register [SEC:UDQ-GOV-STD-001::17.3]
Captures unresolved implementation/documentation gaps.
Suggested ID: `UDQ-PM-LOG-002`

### 17.4 External Reference Register [SEC:UDQ-GOV-STD-001::17.4]
Captures standards, libraries, vendor manuals, cited references.
Suggested ID: `UDQ-EXT-LOG-001`

### 17.5 Baseline Manifest Register [SEC:UDQ-GOV-STD-001::17.5]
Captures each frozen project baseline and included document revisions.
Suggested ID: `UDQ-REL-LOG-001`

---

## 18. Suggested Initial Assignment of Current Docs [SEC:UDQ-GOV-STD-001::18]

### Governance
- `UDQ-GOV-STD-001` — Document Control Scheme
- `UDQ-AUD-SPEC-002` — Placeholder and Anti-Pattern Scan Policy
- `UDQ-AUD-CHK-001` — Local VSCode Review Checklist

### Architecture
- `UDQ-ARCH-NAR-001` — System Controls Narrative
- `UDQ-ARCH-NAR-002` — Platform Controls Narrative

### Requirements
- `UDQ-REQ-MAT-001` — Requirements Traceability Matrix
- `UDQ-QUAL-DEF-001` — Definition of Complete by Subsystem
- `UDQ-QUAL-SPEC-002` — Implementation Proof Model

### Implementation / Gap Control
- `UDQ-GAP-RPT-001` — Open Implementation Gaps

### Release
- `UDQ-AUD-SPEC-001` — Package Audit Specification
- `UDQ-REL-TPL-001` — Release Manifest Template
- `UDQ-REL-TPL-002` — Release Notes and Update Summary Template

### Registers / Logs
- `UDQ-GOV-LOG-001` — Controlled Document Index
- `UDQ-PM-LOG-001` — Decision Log
- `UDQ-REL-LOG-001` — Baseline Manifest Register

---

## 19. Practical Rules for This Project Right Now [SEC:UDQ-GOV-STD-001::19]

Given the current stage, I would use the following immediately:

1. Put every substantive doc under a permanent document ID now.
2. Keep active drafting on `r#` revisions.
3. Add a metadata header and revision history table to every document.
4. Maintain one controlled document index from now on.
5. Freeze coherent sets as baselines rather than treating the folder as the truth.
6. Do not overwrite an older released file; supersede it.
7. Keep templates separate from reports.
8. Treat package notes, audit reports, and weekend-run reports as records.
9. Add document references inside package README or manifest files.
10. Tie code packages to a named document baseline.

---

## 20. Minimum Viable Control Set [SEC:UDQ-GOV-STD-001::20]

If you want a lean implementation first, the minimum viable set is:
- permanent document IDs
- revision/status metadata in each doc
- revision history table in each doc
- controlled document index
- baseline manifest
- no overwrite of released docs

That alone will prevent most chaos.

---

## 21. Expansion Path for Later [SEC:UDQ-GOV-STD-001::21]

As the project grows, this scheme can extend to:
- hardware drawing control
- interface control documents per device/protocol
- supplier document control
- formal verification evidence packages
- release signoff workflows
- field change notices
- deviation/waiver documents
- manufacturing travelers or assembly procedures
- service bulletins

The document ID system above is broad enough to support that without redesign.

---

## 22. Recommendation [SEC:UDQ-GOV-STD-001::22]

Yes: the project needs explicit document control now.

The most useful next controlled document after this scheme would be:
1. the **Controlled Document Index**
2. then revision headers added to the existing narrative and matrix documents
3. then a **Baseline Manifest** for the current precode documentation set
