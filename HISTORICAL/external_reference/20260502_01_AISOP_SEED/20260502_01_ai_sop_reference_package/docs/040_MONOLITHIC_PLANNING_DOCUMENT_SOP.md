---
document_id: DOC-040
title: "SOP: Monolithic Planning Document"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-040
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# SOP: Monolithic Planning Document

SOP: Creating a Monolithic Planning Document Designed for Later Project Formalization
0. Purpose
This SOP defines how to create a large monolithic project document after the preliminary concept review, while avoiding the usual problems of giant documents:
- vague requirements
- buried decisions
- duplicated information
- unclear current vs future behavior
- no extraction path
- no stable IDs
- no way to split into formal docs later
- too much reliance on chat context

The monolithic document is not the final documentation system. It is a structured staging document used to collect the project vision, requirements, workflows, architecture, risks, and implementation plan before splitting them into formal project files.

1. When to Create the Monolithic Document
Create a monolithic planning document after:
1. The concept has been discussed.
2. The user’s goals are reasonably understood.
3. Major workflows are known.
4. Target environment constraints are known.
5. The project is complex enough that coding immediately would create drift.

Do not create the monolithic document before understanding the concept.
Do not start coding serious implementation before the monolithic document exists.
Use this stage for:
- new software projects
- major rewrites
- refactors
- GUI-heavy tools
- hardware/control projects
- data persistence projects
- legacy/offline compatibility projects
- projects that will later need packaging and review

2. Role of the Monolithic Document
The monolithic document is a temporary master planning artifact.
It should answer:
What are we building?
Why are we building it?
Who uses it?
What workflows matter?
What must not break?
What constraints matter?
What does success look like?
What architecture are we aiming for?
What risks exist?
What is the implementation sequence?
How will this eventually be split into project docs?

It should not become:
- a dumping ground
- a code file
- a vague brainstorming transcript
- a substitute for tests
- a substitute for package structure
- a permanent one-file documentation system

3. Required Naming
Use a clear filename:
000_MASTER_PROJECT_PLAN.md

or, if the project is still early:
000_MONOLITHIC_CONCEPT_AND_IMPLEMENTATION_PLAN.md

For a package, place it here:
docs/000_MASTER_PROJECT_PLAN.md

If this document is later split, keep the original as an archived reference:
docs/archive/000_MASTER_PROJECT_PLAN_v001.md

4. Golden Rule
The monolithic document must be written so it can be split later.
That means every major section should include:
- stable section ID
- purpose
- current status
- extraction target
- dependencies
- open questions

Example:
SECTION ID: REQ
Title: Requirements
Later extraction target: docs/010_PRODUCT_REQUIREMENTS.md
Status: Draft / Accepted / Implemented

This lets the document become a staging ground for formal docs instead of becoming a dead-end wall of text.

5. Standard Top-Level Structure
Use this structure.
000_MASTER_PROJECT_PLAN.md

0. Document Control
1. Executive Summary
2. Concept Recap
3. User Context and Workflows
4. Current Baseline / Prototype State
5. Requirements
6. Non-Functional Requirements
7. Data and Persistence Model
8. UI / UX Model
9. Architecture Direction
10. Module Boundary Plan
11. File and Folder Structure Plan
12. Routes / APIs / Interfaces
13. Diagnostics and Testing Plan
14. Risks
15. Technical Debt
16. Decisions
17. Open Questions
18. Implementation Phases
19. Acceptance Criteria
20. Packaging and Handoff Requirements
21. Extraction Plan
22. Appendices

6. Section-by-Section SOP
0. Document Control
Purpose: make the document traceable.
Include:
Document title:
Project name:
Package/run name:
Date:
Author/reviewer:
Source conversation/package:
Current baseline:
Document status:
Version:

Status options:
Draft
Reviewed
Approved for prototype
Approved for implementation
Approved for refactor
Superseded
Archived

Also include:
This document is intended as a monolithic planning document and will later be split into formal project documents.

1. Executive Summary
Purpose: let an independent reviewer understand the project in five minutes.
Include:
- one-paragraph project summary
- target user
- target environment
- current state
- desired end state
- immediate next step
- biggest risks

Keep this concise. The details come later.

2. Concept Recap
Purpose: capture the refined concept after preliminary review.
Include:
What we are building:
Why it matters:
What problem it solves:
What makes this project different:
What prior experiments taught us:
What is now accepted as direction:
What is still exploratory:

Important: distinguish prototype lessons from accepted requirements.
Use labels:
Accepted
Prototype evidence
Still exploratory
Rejected
Deferred

3. User Context and Workflows
Purpose: ground the system in actual use.
For each workflow:
WORKFLOW-001
Name:
User goal:
Starting condition:
Main steps:
Expected result:
Failure modes:
Required feedback:
Priority:

Example:
WORKFLOW-001
Name: Review untested media files
User goal: Work through a large batch quickly.
Starting condition: Files have been scanned but not classified.
Main steps:
1. Open untested queue.
2. View item.
3. Mark tested/broken/type.
4. Move next/random.
Expected result: Status changes are visible and persisted.
Failure modes: Hotkey appears to do nothing; user loses place.
Required feedback: Badge update, confirmation line, radar color update.
Priority: Must

This section later extracts to:
docs/020_USER_WORKFLOWS.md

4. Current Baseline / Prototype State
Purpose: preserve what already works and what was learned.
Include:
Current working package:
Current runnable entrypoint:
Current features:
Known bugs:
Known limitations:
Prototype lessons:
Do-not-break behaviors:

Use a feature inventory format:
FEATURE-001
Name:
Current behavior:
Evidence:
Must preserve? Yes/No
Notes:

This later extracts to:
docs/030_CURRENT_FEATURE_INVENTORY.md

5. Functional Requirements
Purpose: define what the system must do.
Use IDs.
REQ-FUNC-001
Title:
Requirement:
Rationale:
Acceptance test:
Priority: Must / Should / Could
Status: Proposed / Accepted / Implemented / Deferred
Source: user / prototype / inferred / technical necessity

Rules:
- one requirement per item
- avoid compound requirements
- include acceptance test
- mark current vs future
- never bury requirements in prose only

This later extracts to:
docs/010_PRODUCT_REQUIREMENTS.md

6. Non-Functional Requirements
Purpose: define quality constraints.
Categories:
Compatibility
Performance
Reliability
Maintainability
Usability
Diagnostics
Data integrity
Security/safety
Packaging
Offline behavior

Format:
REQ-NF-001
Category:
Requirement:
Rationale:
Verification:
Priority:

Example:
REQ-NF-001
Category: Maintainability
Requirement: Major projects shall include smoke tests and diagnostic harnesses.
Rationale: Testing often happens on machines the assistant cannot access.
Verification: Package includes tools/package_smoke_test.py and tools/diagnostic_harness.py.
Priority: Must

7. Data and Persistence Model
Purpose: describe what the project stores and protects.
Include:
Data objects:
Persistence locations:
Schema/versioning:
Backup behavior:
Migration behavior:
Deletion policy:
Corruption handling:
User data preservation rules:

For each object:
DATA-001
Object:
Purpose:
Fields:
Required fields:
Optional fields:
Storage location:
Lifecycle:
Migration concerns:
Deletion policy:

This later extracts to:
docs/050_DATA_SCHEMA_SPEC.md

8. UI / UX Model
Purpose: define screen behavior before implementation.
Include:
Main screens:
Panel layout:
Primary content area:
Navigation model:
Keyboard shortcuts:
Visible alternatives:
Scrolling behavior:
Persistent settings:
Feedback/confirmation:
Known layout hazards:

For each screen:
UI-001
Screen:
Purpose:
Primary user action:
Layout:
Required controls:
Must be visible without scrolling:
Secondary/collapsible content:
Failure modes:
Acceptance test:

This later extracts to:
docs/070_UI_LAYOUT_SPEC.md

9. Architecture Direction
Purpose: describe where the project is going structurally.
Include:
Current architecture:
Target architecture:
Layer model:
Dependency direction:
Module responsibilities:
What not to couple:
Refactor philosophy:

Example dependency direction:
compat/constants
    ↓
paths/settings/logging
    ↓
catalog/data
    ↓
services/actions
    ↓
views/UI
    ↓
web/server/gui

This later extracts to:
docs/040_ARCHITECTURE_SPEC.md

10. Module Boundary Plan
Purpose: prevent messy extraction later.
For each planned module:
MODULE-001
Name:
Purpose:
Owns:
Does not own:
Public functions/classes:
Depends on:
Used by:
Extraction phase:
Risk:

Example:
MODULE-001
Name: catalog.scanner
Purpose: Discover media files and update catalog presence state.
Owns: recursive scan, new file detection, missing file detection.
Does not own: HTML rendering, GUI dialogs, route handling.
Public functions: scan_media_folder(...)
Depends on: compat, paths, catalog.store, catalog.classification.
Extraction phase: Phase 2.
Risk: High.

This later extracts to:
docs/040_MODULE_BOUNDARY_SPEC.md

11. File and Folder Structure Plan
Purpose: define the intended package structure.
Include:
Package structure:
Runtime data structure:
Source structure:
Docs structure:
Tools structure:
Examples/sample data:
Files that must not be bundled:

Also define:
Zip name convention:
Internal folder convention:
Runtime folder policy:
User data policy:

This later extracts to:
docs/030_FOLDER_STRUCTURE_SPEC.md

12. Routes / APIs / Interfaces
Purpose: define public surfaces.
This applies to:
web routes
CLI commands
GUI actions
file formats
config keys
hardware interfaces
network protocols
plugin APIs

For each interface:
IFACE-001
Type:
Name/path:
Purpose:
Inputs:
Outputs:
Side effects:
Compatibility constraints:
Current/future:
Acceptance test:

This later extracts to:
docs/060_ROUTE_API_INTERFACE_SPEC.md

13. Diagnostics and Testing Plan
Purpose: define how the project proves it works.
Include:
Smoke tests:
Diagnostic harness:
Structure audit:
Dependency audit:
Manual acceptance tests:
Regression tests:
Reports generated:

For each test:
TEST-001
Name:
Purpose:
Command:
Uses real data? Yes/No
Expected output:
Pass criteria:
Failure action:

This later extracts to:
docs/100_ACCEPTANCE_TEST_PLAN.md

and:
docs/105_DIAGNOSTICS_SPEC.md

14. Risks
Purpose: identify possible failures.
Format:
RISK-001
Title:
Likelihood:
Impact:
Affected area:
Detection:
Mitigation:
Fallback:
Status:

This later extracts to:
docs/120_RISK_REGISTER.md

15. Technical Debt
Purpose: identify problems already present.
Format:
DEBT-001
Title:
Location:
Why it is debt:
Impact:
Suggested resolution:
Priority:
Target phase:
Status:

This later extracts to:
docs/130_TECHNICAL_DEBT_REGISTER.md

16. Decisions
Purpose: make design decisions traceable.
Format:
DECISION-001
Date:
Decision:
Context:
Options considered:
Reason:
Consequences:
Revisit trigger:
Status:

This later extracts to:
docs/140_DECISION_LOG.md

17. Open Questions
Purpose: prevent guesses from becoming hidden assumptions.
Format:
QUESTION-001
Question:
Why it matters:
Current assumption:
Evidence needed:
Decision owner:
Status:

This later extracts to:
docs/150_OPEN_QUESTIONS.md

18. Implementation Phases
Purpose: define the work sequence.
For each phase:
PHASE-001
Name:
Goal:
Scope:
Files likely touched:
Behavior expected to change:
Behavior expected unchanged:
Tests required:
Risks:
Rollback:
Exit criteria:

Example:
PHASE-001
Name: Compatibility helper extraction
Goal: Centralize encoding/path/URL helpers.
Scope: Extract helpers only.
Behavior expected to change: None user-facing.
Tests required: compat smoke test, package smoke test.
Exit criteria: App launches and compatibility tests pass.

This later extracts to:
docs/110_IMPLEMENTATION_PLAN.md

19. Acceptance Criteria
Purpose: define done.
Use requirement-linked acceptance items.
ACCEPT-001
Linked requirement:
Test:
Expected result:
Manual/automated:
Required before package delivery? Yes/No
Status:

This section should be strict. If the acceptance criteria are vague, the implementation will drift.

20. Packaging and Handoff Requirements
Purpose: define deliverable standards.
Include:
Package naming:
Internal folder naming:
Required docs:
Required tools:
Required reports:
Runtime data exclusion:
Reviewer onboarding:
Final package report format:

This later extracts to:
docs/160_PACKAGING_AND_HANDOFF_SPEC.md

21. Extraction Plan
Purpose: show how the monolithic document will be split.
This is the key section that makes the monolithic document safe.
Create a table:
Monolithic Section | Extracts To | Owner Layer | Extraction Phase | Status

Example:
5. Functional Requirements | docs/010_PRODUCT_REQUIREMENTS.md | requirements | Phase 0 | Pending
7. Data Model | docs/050_DATA_SCHEMA_SPEC.md | data | Phase 0 | Pending
10. Module Boundaries | docs/040_MODULE_BOUNDARY_SPEC.md | architecture | Phase 0 | Pending
14. Risks | docs/120_RISK_REGISTER.md | risk | Phase 0 | Pending
15. Technical Debt | docs/130_TECHNICAL_DEBT_REGISTER.md | debt | Phase 0 | Pending

Also include:
When this document is split, do not delete it immediately.
Archive it as the originating master plan.

22. Appendices
Use appendices for large supporting material:
Appendix A: Glossary
Appendix B: Example workflows
Appendix C: Screens/layout sketches
Appendix D: Sample schema objects
Appendix E: Prototype notes
Appendix F: Rejected ideas
Appendix G: Historical package timeline

Avoid burying core requirements in appendices.

7. Writing Rules for the Monolithic Document
Use stable IDs
Every important item gets an ID:
REQ-FUNC-001
REQ-NF-001
WORKFLOW-001
DATA-001
UI-001
MODULE-001
RISK-001
DEBT-001
DECISION-001
QUESTION-001
PHASE-001
ACCEPT-001

Stable IDs allow later references across documents.

Mark current vs future
Every feature/requirement should be labeled:
Current
Accepted
Planned
Prototype-only
Deferred
Rejected
Unknown

This avoids confusing what exists with what is desired.

Avoid long unstructured prose
Use prose for summaries, but use structured blocks for decisions, requirements, risks, and tests.
Bad:
The app should probably keep track of files and not lose stuff.

Good:
REQ-DATA-002
Requirement: The app shall not automatically delete catalog records when files are missing.
Rationale: External media may be disconnected temporarily.
Acceptance: Remove a file, rescan, confirm metadata remains.
Priority: Must.

Do not duplicate truth
The monolithic document can summarize, but avoid repeating detailed requirements in multiple places.
Use references:
See REQ-DATA-002.
See WORKFLOW-003.
See RISK-004.

Use “extraction target” notes
At the top of each section:
Extraction target:
docs/010_PRODUCT_REQUIREMENTS.md

This makes splitting easier.

Preserve rejected ideas
Do not just delete discarded directions.
Record them in:
Rejected / Deferred Ideas

Format:
REJECTED-001
Idea:
Reason rejected:
Could revisit if:

This prevents old ideas from being accidentally reintroduced later.

8. Anti-Patterns to Avoid
Anti-pattern 1: The wall of prose
A giant narrative that no one can audit.
Fix: use stable IDs and structured blocks.

Anti-pattern 2: Requirements mixed with implementation
Bad:
Use function scan_files() to update the table and then reload the browser.

Better:
Requirement: The app shall update the catalog when the user scans.
Implementation note: Current prototype uses scan_files().

Keep requirements and implementation separate.

Anti-pattern 3: Current and future behavior mixed together
Bad:
The app has ordered playlists.

when it only has label-based playlists now.
Fix:
Current: playlist membership is label-based.
Future: ordered playlists are planned.

Anti-pattern 4: No acceptance tests
A requirement without a test is a wish.
Every Must requirement needs an acceptance test.

Anti-pattern 5: No extraction plan
If the monolithic document has no split plan, it will become permanent debt.

Anti-pattern 6: No decision log
If decisions are not recorded, the project will revisit the same debates repeatedly.

Anti-pattern 7: Burying risk
Risk must be explicit. Do not hide it inside prose.

9. Review Procedure for the Monolithic Document
Before coding, review the document using this checklist:
[ ] Concept is clear.
[ ] User workflows are clear.
[ ] Target environment is explicit.
[ ] Requirements have IDs.
[ ] Must requirements have acceptance tests.
[ ] Non-goals are listed.
[ ] Current vs future behavior is labeled.
[ ] Data persistence rules are clear.
[ ] UI layout rules are clear, if applicable.
[ ] Architecture direction is clear.
[ ] Module boundaries are proposed.
[ ] Risks are listed.
[ ] Debt is listed.
[ ] Decisions are recorded.
[ ] Open questions are listed.
[ ] Implementation phases are sequenced.
[ ] Packaging/handoff expectations are clear.
[ ] Extraction plan exists.

If this checklist fails, revise the document before coding.

10. When to Split the Monolithic Document
Split it when:
- the concept is stable,
- the requirements are accepted,
- the project is entering implementation/refactor,
- the document is too large to review efficiently,
- multiple reviewers or agents need specific docs,
- the package needs durable structure.

Do not split too early if the concept is still moving quickly.
Do not split too late if implementation is about to begin.

11. Splitting Procedure
When ready, split into:
docs/000_README_START_HERE.md
docs/010_PRODUCT_REQUIREMENTS.md
docs/020_USER_WORKFLOWS.md
docs/030_CURRENT_FEATURE_INVENTORY.md
docs/040_ARCHITECTURE_SPEC.md
docs/050_MODULE_BOUNDARY_SPEC.md
docs/060_DATA_SCHEMA_SPEC.md
docs/070_ROUTE_API_INTERFACE_SPEC.md
docs/080_UI_LAYOUT_SPEC.md
docs/090_DIAGNOSTICS_AND_TESTING_SPEC.md
docs/100_ACCEPTANCE_TEST_PLAN.md
docs/110_IMPLEMENTATION_PLAN.md
docs/120_RISK_REGISTER.md
docs/130_TECHNICAL_DEBT_REGISTER.md
docs/140_DECISION_LOG.md
docs/150_OPEN_QUESTIONS.md
docs/160_PACKAGING_AND_HANDOFF_SPEC.md

Then archive the original:
docs/archive/000_MASTER_PROJECT_PLAN_v001.md

Add a note:
This monolithic plan was split into formal documents on YYYY-MM-DD.
The formal docs are now authoritative.
This archived file is retained for historical context.

12. Definition of Done for the Monolithic Document
The monolithic document is complete when an independent reviewer can answer:
What is the project?
Who uses it?
What workflows matter?
What exists now?
What must be built?
What must not break?
What constraints matter?
What data must be preserved?
What does the UI need to do?
What architecture are we aiming for?
What risks and debt exist?
What is the implementation sequence?
How will we test it?
How will we package it?
How will this document be split later?

If the reviewer needs chat history to answer those, the document is not complete.

13. Minimal Template
Use this when creating the document quickly:
# 000_MASTER_PROJECT_PLAN

## 0. Document Control
## 1. Executive Summary
## 2. Concept Recap
## 3. User Workflows
## 4. Current Baseline / Prototype State
## 5. Functional Requirements
## 6. Non-Functional Requirements
## 7. Data and Persistence Model
## 8. UI / UX Model
## 9. Architecture Direction
## 10. Module Boundary Plan
## 11. File and Folder Structure Plan
## 12. Routes / APIs / Interfaces
## 13. Diagnostics and Testing Plan
## 14. Risk Register
## 15. Technical Debt Register
## 16. Decision Log
## 17. Open Questions
## 18. Implementation Phases
## 19. Acceptance Criteria
## 20. Packaging and Handoff Requirements
## 21. Extraction Plan
## 22. Appendices

14. Short Version
The monolithic document is allowed, but it must be:
structured
ID-based
reviewable
extractable
clear about current vs future
linked to acceptance tests
explicit about risks and debt
designed to be split later

The goal is not to avoid monolithic documents entirely.
The goal is to make the monolithic document a controlled staging artifact instead of a documentation swamp.
