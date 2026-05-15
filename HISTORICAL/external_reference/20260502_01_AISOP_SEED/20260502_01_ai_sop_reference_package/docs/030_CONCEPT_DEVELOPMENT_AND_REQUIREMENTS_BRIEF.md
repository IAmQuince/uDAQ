---
document_id: DOC-030
title: "Concept Development and Requirements Brief"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-030
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Concept Development and Requirements Brief

000_CONCEPT_DEVELOPMENT_AND_REQUIREMENTS_BRIEF.md
Purpose
This document captures the project concept before implementation begins.
It exists to prevent rushed coding, feature drift, vague requirements, and context loss. Before any code is written or modified, the project team should use this document to define the intended product, user workflows, constraints, acceptance criteria, risks, and boundaries.
This document should be readable by an independent reviewer who has no access to the original chat history.

1. Project Identity
Project name:

Package/run name:

Date:

Author / reviewer:

Current phase:
[ ] Concept
[ ] Prototype
[ ] Architecture baseline
[ ] Refactor
[ ] Feature implementation
[ ] Bug fix
[ ] Release candidate
[ ] Maintenance

Current baseline package, if any:

Previous related packages:

Is this a new project or continuation?
[ ] New project
[ ] Continuation
[ ] Rebuild from prototype
[ ] Refactor of working baseline

2. Plain-Language Concept
Describe the project in normal language.
What are we building?

Who is it for?

What problem does it solve?

What does the user actually do with it?

Why does this project need to exist?

Example style:
This project is a local media archive browser for an offline legacy Windows XP machine. It allows the user to scan an external media folder, browse Flash/video/image files, track whether files work, classify Flash files as games/videos/animations, build playlists, and navigate the collection visually.

3. User and Workflow Context
Define the actual user situation.
Primary user:

User skill level:

Expected environment:

Typical session:

What does the user care about most?

What frustrates the user today?

What should the software make easier?

What should the software avoid making harder?

For each major workflow:
Workflow name:

Starting condition:

User goal:

Steps the user expects:

Successful outcome:

Failure outcome to avoid:

Required feedback/confirmation:

Example:
Workflow: Review unknown Flash files

Starting condition:
The user has imported hundreds or thousands of SWF files.

Goal:
Quickly determine which ones work and whether they are games, videos, animations, broken, or unsupported.

Expected steps:
Open Flash library.
Start reviewing untested Flash.
View one file at a time.
Use keyboard or visible buttons to mark status/type.
Move to next/random item.
See the metadata and radar update.

Successful outcome:
The user can classify many files quickly without losing place.

Failure outcome:
The user is unsure whether a hotkey worked, the item does not update, or the media stage is pushed offscreen.

4. Current Pain Points
List what is wrong with the current state or prior prototype.
Pain point 001:
Description:
Evidence:
Why it matters:
Current workaround:
Desired improvement:
Priority:

Examples:
Pain point:
Metadata badges above the media stage stack vertically and push the video down.

Why it matters:
The main media should be visible immediately. The current layout makes the user scroll before seeing the content.

Desired improvement:
Use a compact one-line media header with small badges.

5. Desired Outcomes
Define success in concrete terms.
At the end of this project/run, the user should be able to:

1.
2.
3.
4.
5.

Also define non-goals:
This project/run will not attempt to:

1.
2.
3.

This section is important because it stops scope creep.
Example:
This run will create documentation and structure only. It will not extract source modules yet.

6. Functional Requirements
Use requirement IDs.
Format:
REQ-FUNC-001
Title:
Requirement:
Rationale:
Acceptance test:
Priority: Must / Should / Could
Status: Proposed / Accepted / Implemented / Deferred

Example:
REQ-FUNC-001
Title: Preserve missing file records
Requirement:
The app shall not delete catalog records automatically when files are missing from the media folder.

Rationale:
The user may temporarily disconnect a drive or move media. Metadata, playlists, notes, and import positions must not be lost.

Acceptance test:
Remove a file from the media folder, rescan, and verify the catalog record remains with a missing status.

Priority:
Must

Status:
Accepted

7. Non-Functional Requirements
These define quality, compatibility, maintainability, performance, and safety.
Suggested categories:
Compatibility
Performance
Reliability
Data integrity
Maintainability
Usability
Diagnostics
Packaging
Security/safety
Offline behavior

Format:
REQ-NF-001
Category:
Requirement:
Rationale:
Verification method:
Priority:

Example:
REQ-NF-001
Category: Compatibility
Requirement:
The project shall remain compatible with Python 2.7.6 on Windows XP unless explicitly approved otherwise.

Rationale:
The target machine is a legacy XP environment.

Verification:
Run syntax/import smoke test under Python 2.7.6.

Priority:
Must

8. Environment and Compatibility Constraints
This should be explicit before code.
Target OS:

Target Python/runtime:

Target browser/GUI/runtime:

Hardware constraints:

Offline/online assumptions:

Allowed dependencies:

Forbidden dependencies:

Installation assumptions:

File transfer assumptions:

Performance constraints:

Screen size/display assumptions:

Example:
Target OS:
Windows XP 32-bit SP3

Target Python:
Python 2.7.6

Browser:
RetroZilla / old Gecko

Forbidden:
Python 3-only syntax, Flask, pathlib, f-strings, CSS Grid, modern JS-only layout.

9. Data Model and Persistence Requirements
Before code, define what data exists and what must be preserved.
What data does the project store?

Where is it stored?

What user data must never be lost?

What files are runtime-generated?

What files are source/package files?

What should be backed up before migration?

What should happen if data is missing/corrupt?

What schema/versioning is needed?

Format for key data objects:
Object:
Purpose:
Fields:
Required fields:
Optional fields:
Persistence location:
Migration concerns:
Deletion policy:

Example:
Object:
Catalog item

Purpose:
Represents one media file and its user metadata.

Required preservation:
ID, path history, status, content kind, notes, playlists, favorite, import index.

Deletion policy:
Do not delete automatically when media file is missing.

10. UI / UX Requirements
Before coding UI, define layout principles.
Primary screen:

Main user focus:

Navigation model:

Panel layout:

What should be visible without scrolling?

What can be secondary/collapsible?

What keyboard shortcuts are required?

What visible alternatives are required?

What feedback confirms user actions?

What layout mistakes must be avoided?

Example:
The media stage must dominate the viewer.
Navigation belongs on the left.
Radar/details belong on the right.
Quick mark controls belong below the media.
Metadata badges must be compact and must not push the media below the fold.

11. Workflow and State Requirements
Define how the software remembers state.
What should persist between sessions?

What should reset each session?

What user choices should be remembered?

What should happen after restart?

What should happen if paths change?

What should happen if external media is disconnected?

Example:
The selected media folder should persist between sessions. If it is unavailable after restart, the app should warn the user rather than deleting catalog entries.

12. Diagnostics and Observability Requirements
Define diagnostics before implementation.
What failures are likely?

What should be logged?

What diagnostic reports should be generated?

What should a user be able to copy/paste back?

What should be visible in the UI?

What should the smoke test verify?

Required diagnostic outputs:
diagnostic_harness_report.txt
structure_audit_report.txt
package_smoke_test_report.txt
compat_smoke_test_report.txt, if applicable

Diagnostic report should include:
runtime version
OS/platform
package path
working directory
config path
data path
dependency/import checks
test media scan result
current errors
tracebacks
pass/fail summary

13. Acceptance Criteria
Define success before code.
ACCEPT-001
Requirement linked:
Test:
Expected result:
Manual or automated:
Pass/fail:

Example:
ACCEPT-001
Requirement linked:
REQ-UI-001

Test:
Open a media item in the viewer on a 1024x768 display.

Expected result:
The media stage is visible without scrolling.

Manual or automated:
Manual

14. Risks and Mitigations
Before implementation, list risks.
RISK-001
Title:
Likelihood:
Impact:
Affected area:
Detection method:
Mitigation:
Fallback/rollback:
Status:

Example:
RISK-001
Title:
Python 2 Unicode/path regression

Likelihood:
Medium

Impact:
High

Detection:
Run compat smoke test with spaces, punctuation, and non-ASCII filenames.

Mitigation:
Route all text/path/URL conversion through compatibility helpers.

Fallback:
Restore prior working package.

15. Technical Debt Known at Start
This is different from risks. Debt is already present.
DEBT-001
Title:
Location:
Why it is debt:
Impact:
Suggested resolution:
Priority:
Phase:
Status:

Example:
DEBT-001
Title:
Monolithic app file

Location:
xp_retroweb_browser_app.py

Why it is debt:
Catalog, routing, UI rendering, scanning, radar, and GUI logic are mixed together.

Impact:
Feature changes are risky and hard to review.

Suggested resolution:
Extract in staged phases after docs and acceptance tests are frozen.

Priority:
High

16. Architecture Direction
Before coding, define intended architecture.
Current architecture:

Target architecture:

Layer boundaries:

What belongs in each layer:

What must not cross layers:

Planned extraction sequence:

Modules not to touch yet:

Example:
catalog.scanner shall not render HTML.
views.viewer shall not scan the filesystem.
radar.lenses shall not mutate catalog data.
web.router shall not directly edit catalog fields except through actions/store.

17. Package / File Structure Plan
Define the expected structure before creating files.
Package name:

Internal folder name:

Required top-level files:

Required docs:

Required tools:

Required source folders:

Runtime folders:

Folders/files that should not be included:

Example:
The zip filename and internal top-level folder must match.
Runtime AppData should not be bundled unless explicitly included for debugging.
Real user media files should not be included.

18. Implementation Boundaries for This Run
This section prevents scope creep.
This run will change:

This run will not change:

Files expected to change:

Files explicitly not to change:

Behavior expected to change:

Behavior expected unchanged:

Tests required before delivery:

Rollback plan:

Example:
This run will:
Create docs and folder skeleton.

This run will not:
Extract source modules or change app behavior.

19. Open Questions
If something is unknown, write it down instead of guessing.
QUESTION-001
Question:
Why it matters:
Current assumption:
Needed evidence:
Decision needed by:
Status:

Example:
QUESTION-001
Question:
Should playlists be ordered lists or item labels?

Why it matters:
This affects catalog schema and viewer queue behavior.

Current assumption:
Manual playlists should eventually be ordered lists, but current implementation may be label-based.

Needed evidence:
Inspect current catalog structure and playlist routes.

20. Decision Log
Record design decisions before and during implementation.
DECISION-001
Date:
Decision:
Context:
Options considered:
Reason:
Consequences:
Revisit trigger:

Example:
DECISION-001
Decision:
Use package-local AppData instead of storing catalog inside the selected media folder.

Reason:
Prevents accidental modification of user media folders and keeps app runtime data portable.

Consequence:
Running a different package folder creates a different AppData unless migrated.

21. Pre-Code Review Checklist
No code should be written until this checklist is complete.
[ ] Project concept written.
[ ] User workflow described.
[ ] Target environment defined.
[ ] Functional requirements drafted.
[ ] Non-functional requirements drafted.
[ ] Data persistence requirements drafted.
[ ] UI/UX requirements drafted, if applicable.
[ ] Acceptance criteria written.
[ ] Risks identified.
[ ] Existing technical debt identified.
[ ] Package/folder structure planned.
[ ] Implementation scope defined.
[ ] Non-goals defined.
[ ] Open questions listed.
[ ] Current baseline identified.
[ ] Rollback plan defined.

If the project is exploratory/prototype work, mark it as such:
This is prototype work. Requirements may change.

If the project is production/refactor work, require the checklist.

22. Final Concept Approval Section
Before implementation, explicitly approve the concept.
Concept status:
[ ] Draft
[ ] Reviewed
[ ] Approved for prototype
[ ] Approved for implementation
[ ] Approved for refactor
[ ] Rejected / needs revision

Reviewer notes:

Approved scope:

Deferred items:

Do-not-touch items:

Next package/run name:

How This Fits Into the Overall Workflow
This document should happen before the zip-package SOP.
The sequence becomes:
1. Concept Development Brief
2. Requirements / Acceptance Criteria
3. Package Structure Plan
4. Implementation or refactor
5. Zip package
6. Package intake/review SOP
7. Audit / tests / debt register
8. Next concept/update brief

So the package-review SOP answers:
What do we do when opening an existing package?

This concept document answers:
What do we do before creating or changing a package?

Recommended file name
I would use:
000_CONCEPT_DEVELOPMENT_AND_REQUIREMENTS_BRIEF.md

And every serious package should include the latest version in:
docs/000_CONCEPT_DEVELOPMENT_AND_REQUIREMENTS_BRIEF.md

For smaller projects, a shortened version can be used, but for anything involving architecture, hardware, legacy systems, GUIs, data persistence, or refactoring, the full document is worth it.
