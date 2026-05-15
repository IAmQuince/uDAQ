---
document_id: DOC-070
title: "SOP: ZIP Package Review and Handoff"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-070
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# SOP: ZIP Package Review and Handoff

Below is a generalized SOP you can use for Codex, me, or any other AI/software assistant working inside a zipped software package.

SOP: Deterministic Workflow for Reviewing, Modifying, and Packaging a Software Project
0. Purpose
The purpose of this SOP is to make software projects portable, reviewable, and independent of any one AI conversation context.
A zipped package should contain enough information for an independent reviewer to understand:
What this project is
What version/package this is
What works now
What changed
What must not break
How to run it
How to test it
What risks remain
What technical debt exists
What the next safe step is

No project should depend on an AI remembering private context from a previous chat. The package itself should carry the context.

1. Golden Rule
Before changing code:
Inspect the actual package.
Read the project documents.
Identify the runnable baseline.
Run available tests.
Record what you found.
Only then modify anything.

Do not infer the project state from memory, package name, README claims, or prior conversation alone.

2. Standard Package Structure
A professional zipped package should generally use this structure:
yyyymmdd_00_description-of-run/
├── README_START_HERE.txt
├── RUN_INSTRUCTIONS.txt
├── TEST_INSTRUCTIONS.txt
├── CHANGELOG.txt
├── KNOWN_LIMITATIONS.txt
│
├── app_or_project_entrypoint.py
├── launchers/
│   └── optional launch scripts
│
├── src/ or project_package/
│   └── actual source code
│
├── docs/
│   ├── 010_PRODUCT_REQUIREMENTS.txt
│   ├── 020_CURRENT_FEATURE_INVENTORY.txt
│   ├── 030_FOLDER_STRUCTURE_SPEC.txt
│   ├── 040_MODULE_BOUNDARY_SPEC.txt
│   ├── 050_DATA_SCHEMA_SPEC.txt
│   ├── 060_ROUTE_API_PAGE_SPEC.txt
│   ├── 070_UI_LAYOUT_SPEC.txt
│   ├── 080_ACCEPTANCE_TEST_PLAN.txt
│   ├── 090_RISK_REGISTER.txt
│   ├── 100_TECHNICAL_DEBT_REGISTER.txt
│   ├── 110_REFACTOR_SEQUENCE_PLAN.txt
│   ├── 120_DECISION_LOG.txt
│   └── 130_REVIEWER_ONBOARDING.txt
│
├── tools/
│   ├── diagnostic_harness.py
│   ├── package_smoke_test.py
│   ├── structure_audit.py
│   ├── dependency_audit.py
│   └── debt_audit.py
│
├── tests/
│   └── optional automated tests
│
├── examples/
│   └── optional sample data
│
└── runtime_data/
    └── usually excluded unless explicitly intended

For small or legacy projects, this structure can be simplified, but the package must still include:
README_START_HERE
CHANGELOG
RUN_INSTRUCTIONS
TEST_INSTRUCTIONS
FEATURE_INVENTORY
ACCEPTANCE_TEST_PLAN
RISK_REGISTER
TECHNICAL_DEBT_REGISTER
diagnostic_harness
smoke_test

3. First-Pass Intake Procedure
When opening a zipped package, proceed in this order.
Step 1 — Record package identity
Before reading code, record:
Zip filename:
Internal top-level folder:
Do they match?
Timestamp/version:
App/package version string:
Main entry point:
Target OS:
Target language/runtime:
Known constraints:

If the zip name and internal folder name do not match, record it as a traceability issue.
Step 2 — Inspect top-level structure
Run or manually perform a structure inventory:
List top-level files/folders
Identify app entry point
Identify docs folder
Identify tools folder
Identify source folder
Identify tests folder
Identify runtime data folders
Identify accidental user/private files

Do not modify yet.
Step 3 — Read documents in deterministic order
Read docs in this order:
1. README_START_HERE
2. RUN_INSTRUCTIONS
3. TEST_INSTRUCTIONS
4. CHANGELOG
5. PRODUCT_REQUIREMENTS
6. CURRENT_FEATURE_INVENTORY
7. FOLDER_STRUCTURE_SPEC
8. MODULE_BOUNDARY_SPEC
9. DATA_SCHEMA_SPEC
10. ROUTE_API_PAGE_SPEC
11. UI_LAYOUT_SPEC
12. ACCEPTANCE_TEST_PLAN
13. RISK_REGISTER
14. TECHNICAL_DEBT_REGISTER
15. REFACTOR_SEQUENCE_PLAN
16. DECISION_LOG
17. REVIEWER_ONBOARDING

While reading, classify each statement as:
Current behavior
Planned behavior
Aspirational behavior
Unknown/unverified
Contradicted by code

Documentation must be treated as a claim until verified against code and tests.
Step 4 — Identify target environment constraints
Record constraints explicitly:
Python version
OS
Browser/runtime
GUI toolkit
Hardware dependencies
Network/offline assumptions
External tools
Required packages
Forbidden packages
Legacy compatibility requirements

If the project targets a legacy environment, do not run modernization changes casually.
Step 5 — Run non-invasive audits first
Before running the app, run audits that should not mutate project data:
structure_audit
dependency_audit
syntax/import check
package_smoke_test if it uses temp data only
diagnostic_harness if safe

If any tool mutates real user data, do not run it until its behavior is understood.

4. Required Intake Notes
After intake, create or update:
docs/INTAKE_REVIEW_NOTES.txt

This should include:
Package reviewed:
Date/time reviewed:
Reviewer:
Environment used:
Documents found:
Documents missing:
Entry point found:
Tests found:
Tests run:
Tests passed:
Tests failed:
Main risks:
Immediate blockers:
Recommended next step:

If the package does not include this file, create it.

5. Source Code Review Procedure
After reading the docs and running safe audits, inspect the source.
Step 1 — Identify architectural layers
Classify files/functions into layers:
compatibility/helpers
paths/config/settings
logging/diagnostics
data model/schema
storage/persistence
scanner/parser/importer
business logic/actions
routing/API/controller
views/UI/rendering
visualization/radar/charts
GUI/admin shell
entrypoint/launcher
tests/tools

If a file contains many layers, record it as monolithic debt.
Step 2 — Build a module/function map
Create or update:
docs/MODULE_FUNCTION_MAP.txt

Include:
File
Major functions/classes
Layer
Responsibilities
Known callers
Known side effects
Extraction candidate?
Risk level

Example:
File: xp_app.py
Function: scan_files()
Layer: scanner/catalog
Responsibilities: walk media folder, detect files, update catalog
Side effects: mutates catalog, writes batch data
Risk: high
Extraction candidate: yes, later

Step 3 — Identify public interfaces
Before refactoring, identify public interfaces:
entry points
CLI arguments
GUI buttons/actions
route URLs
file formats
config keys
catalog schema fields
function/class APIs already used across files
diagnostic output format

These must not change accidentally.
Create or update:
docs/API_INTERFACE_FREEZE.txt

Even if the project has no formal API, its file formats, launchers, routes, and user-visible actions are interfaces.

6. Debt Registers
Every package should maintain debt registries. Debt must be explicit, searchable, and prioritized.
6.1 Technical Debt Register
File:
docs/100_TECHNICAL_DEBT_REGISTER.txt

Suggested format:
DEBT-001
Title:
Category:
Severity: Low / Medium / High / Critical
Location:
Current behavior:
Why it is debt:
Risk if ignored:
Suggested fix:
Blocking future work?
Owner/phase:
Status: Open / In Progress / Resolved / Deferred

Categories:
Architecture
Compatibility
Encoding/Unicode
Path handling
Data integrity
Persistence
Performance
UI layout
Testing
Documentation
Security/safety
Error handling
Packaging

6.2 Risk Register
File:
docs/090_RISK_REGISTER.txt

Format:
RISK-001
Title:
Likelihood:
Impact:
Detection method:
Mitigation:
Fallback/rollback:
Status:

Risks are things that may happen. Debt is something already present.
6.3 Decision Log
File:
docs/120_DECISION_LOG.txt

Format:
DECISION-001
Date:
Decision:
Context:
Options considered:
Reason:
Consequences:
Revisit trigger:

Use this for choices like:
Use JSON instead of SQLite for now.
Keep Python 2.7 compatibility.
Do not extract views before catalog store.
Use package-local AppData.

6.4 Open Questions Register
File:
docs/OPEN_QUESTIONS.txt

Format:
QUESTION-001
Question:
Why it matters:
Current assumption:
Needed evidence:
Owner:
Status:

Use this instead of guessing.

7. Audit Procedure
A package should include audit scripts where practical.
7.1 Structure audit
Tool:
tools/structure_audit.py

Checks:
expected files exist
expected folders exist
docs present
tools present
entry point present
launchers present
source package present
no forbidden runtime folders accidentally included
zip/internal folder naming convention

Output:
structure_audit_report.txt

7.2 Dependency audit
Tool:
tools/dependency_audit.py

Checks:
imports used
standard library vs external
target-runtime incompatible imports
Python-version-incompatible syntax if possible
missing optional dependencies

For legacy targets, this is critical.
7.3 Feature inventory audit
Tool or manual checklist:
tools/feature_audit.py

Checks current features against:
docs/020_CURRENT_FEATURE_INVENTORY.txt

This is how feature loss is caught.
7.4 Debt audit
Tool:
tools/debt_audit.py

Checks:
TODO
FIXME
HACK
temporary
placeholder
not implemented
pass  # suspicious
broad except
silent except
hardcoded paths

Output should append candidates to the debt register or produce a review list.

8. Working on a Package: Change Discipline
Step 1 — Define the exact task type
Every run should be classified as one of:
documentation only
structure only
diagnostic/test only
bug fix
UI polish
feature addition
compatibility fix
schema migration
module extraction/refactor
packaging cleanup

Do not mix too many task types unless explicitly approved.
Step 2 — Define scope
Before editing:
Files expected to change:
Files explicitly not to change:
Behavior expected to change:
Behavior expected unchanged:
Tests required:
Rollback plan:

Record this in:
docs/WORKPLAN_CURRENT_RUN.txt

Step 3 — Make the smallest safe change
Do not opportunistically rewrite unrelated code.
If a better idea appears, record it in the debt register or future plan, not in the current patch, unless it is essential.
Step 4 — Update docs as code changes
Any change to behavior must update:
CHANGELOG
FEATURE_INVENTORY if feature changes
ACCEPTANCE_TEST_PLAN if test expectations change
SCHEMA_SPEC if data format changes
ROUTE_SPEC if routes change
UI_SPEC if layout changes
RISK_REGISTER if new risk appears
TECHNICAL_DEBT_REGISTER if debt is added/removed

Docs must not lag code.

9. Refactor Workflow
Refactoring must be staged.
9.1 Before extraction
Before moving code into modules:
1. Identify exact functions/classes to move.
2. Identify all callers.
3. Freeze function signatures.
4. Add smoke tests covering the behavior.
5. Add compatibility shim if old call path must remain.
6. Record expected unchanged behavior.
7. Commit/package only after tests pass.

9.2 Extraction order
Preferred order:
1. Compatibility helpers
2. Paths/config/settings
3. Logging/diagnostics
4. Schema/data model/store
5. Scanner/parser/import logic
6. Actions/service logic
7. Web routing/responses
8. Views/UI rendering
9. Specialized visualization engines
10. GUI/admin shell
11. Thin entrypoint

9.3 Extraction acceptance gate
Each extraction phase must prove:
app still launches
baseline tests pass
no feature inventory loss
diagnostic harness passes
package audit passes
changed files documented
rollback possible

Do not proceed to the next phase until the current one is accepted.

10. Independent Reviewer Handoff
Every package should allow an independent reviewer to get up to speed in under 30 minutes.
Include:
docs/130_REVIEWER_ONBOARDING.txt

Suggested structure:
1. What this project does
2. Target environment
3. How to run it
4. How to test it
5. Current package purpose
6. What changed in this package
7. What did not change
8. Current architecture map
9. Most important files
10. Known risks
11. Known technical debt
12. What to review first
13. Expected test results
14. Next planned task
15. What not to touch yet

Also include:
docs/PACKAGE_MANIFEST.txt

Format:
File/folder
Purpose
Required?
Generated or source?
Safe to delete?
Notes

This prevents reviewers from guessing which files matter.

11. Context Preservation Rules
A package must preserve context explicitly.
Do not rely on:
previous AI conversation
memory
chat history
unwritten assumptions
package name alone
README claims alone

Instead, encode context into:
README_START_HERE
CHANGELOG
FEATURE_INVENTORY
DECISION_LOG
RISK_REGISTER
TECHNICAL_DEBT_REGISTER
REFACTOR_SEQUENCE_PLAN
INTAKE_REVIEW_NOTES

Every package should answer:
Why does this package exist?
What state was it based on?
What changed?
What is intentionally unchanged?
What is the next safe move?

12. Changelog Standard
File:
CHANGELOG.txt

Every entry should include:
Package/version:
Date:
Purpose:
Changed files:
Behavior changes:
Non-behavioral changes:
Tests run:
Known limitations:
Risks introduced:
Risks reduced:
Next recommended step:

Avoid vague entries like:
Updated app.
Fixed bugs.
Improved UI.

Use specific entries like:
Moved Unicode/path helpers from xp_app.py into retroweb.compat.
Updated xp_app.py imports.
Added compat_smoke_test.py.
No catalog, router, viewer, or radar extraction performed.

13. Test Report Standard
Every package should include test reports generated by tools or manually written.
Recommended:
test_reports/
├── structure_audit_report.txt
├── package_smoke_test_report.txt
├── diagnostic_harness_report.txt
├── compat_smoke_test_report.txt
└── manual_acceptance_report.txt

If reports are not bundled, the README should say how to generate them.
Each report should include:
tool name
timestamp
environment
command run
pass/fail summary
detailed failures
tracebacks if any
next action

14. Diagnostic Harness Standard
A diagnostic harness should be able to run without damaging real user data.
It should:
use temp folders
avoid real catalog unless explicitly requested
write a report file
not require internet
not require hardware unless testing hardware-specific project
print clear pass/fail summary
capture exceptions

It should report:
runtime version
platform
working directory
package root
expected files
import tests
config paths
data paths
sample read/write
core function smoke checks
route/render checks if relevant
cleanup result

15. Handling User Data and Runtime Data
Packages should generally not include real runtime data.
Do not accidentally include:
real media files
real logs with private paths
real catalogs with personal metadata
API keys
credentials
cache folders
large generated files
personal documents

If sample data is needed, place it in:
examples/

and make it clearly fake.
If runtime data must be included for debugging, document it explicitly:
docs/DEBUG_DATA_INCLUDED.txt

16. Versioning and Naming
Use package naming:
yyyymmdd_00_description-of-run.zip

Internal top-level folder must match:
yyyymmdd_00_description-of-run/

The app should expose a version string matching the package purpose.
Example:
Package:
20260503_03_project_bootstrap_compat_verified.zip

Internal folder:
20260503_03_project_bootstrap_compat_verified/

App version:
20260503_03_project_bootstrap_compat_verified

If the app version intentionally differs, document why.

17. Self-Audit Before Finalizing a Package
Before delivering a package, run this checklist.
Structure
Zip name matches internal folder.
README_START_HERE exists.
RUN_INSTRUCTIONS exists.
TEST_INSTRUCTIONS exists.
CHANGELOG exists.
docs folder exists.
tools folder exists.
entry point exists.
no accidental runtime/user files.

Behavior
Runnable entry point still works.
Launchers still point to correct files.
Smoke tests pass.
Diagnostic harness passes.
Manual acceptance checklist updated.
Feature inventory not reduced unintentionally.

Documentation
Changelog lists changed files.
Known limitations updated.
Risk register updated.
Technical debt register updated.
Refactor plan updated.
Reviewer onboarding updated.

Compatibility
Target runtime syntax respected.
No forbidden dependencies introduced.
No modern-only APIs introduced.
Legacy/offline constraints respected.

Traceability
Package purpose clear.
Previous baseline identified.
Next step identified.
All intentional non-changes documented.

18. Final Package Report Format
When returning a package, always provide:
Package:
Internal folder:
Based on:
Purpose:
Changed files:
Unchanged important files:
Tests run:
Test results:
Known limitations:
Risks:
Debt added:
Debt resolved:
Feature removals:
Broad refactor performed? yes/no
Next recommended step:

Example:
Package:
20260503_03_project_bootstrap_compat_verified.zip

Internal folder:
20260503_03_project_bootstrap_compat_verified

Based on:
20260503_02_truth_pass_compat_start

Purpose:
Clean project identity and verify compat extraction.

Changed files:
...

Tests run:
structure_audit.py PASS
compat_smoke_test.py PASS
package_smoke_test.py PASS

Feature removals:
None intended.

Broad refactor:
No.

Next:
Begin paths.py extraction only after XP acceptance.

19. What Not to Do
Do not:
change code before inspecting docs and current files
assume docs are true without checking code
rewrite broad areas casually
remove existing features silently
modernize legacy code without permission
introduce dependencies casually
collapse multiple phases into one package
ship without tests
ship without changelog
ship with mismatched package/folder names
include private runtime data accidentally
leave context only in chat

20. Definition of a Healthy Package
A healthy package is one where an independent reviewer can answer these without asking the original AI:
What is this?
How do I run it?
How do I test it?
What changed?
What must not break?
What are the risks?
What debt exists?
What files matter?
What is the next step?
What should I avoid touching?

If those answers are not inside the package, the package is not complete.

21. Minimal SOP Checklist for Every Run
For quick use, every run should follow this checklist:
[ ] Unzip and record package identity.
[ ] Confirm zip/internal folder naming.
[ ] Read README_START_HERE.
[ ] Read CHANGELOG.
[ ] Read FEATURE_INVENTORY.
[ ] Read ACCEPTANCE_TEST_PLAN.
[ ] Run structure audit.
[ ] Run smoke tests.
[ ] Inspect actual changed/current files.
[ ] Define task scope.
[ ] Update WORKPLAN_CURRENT_RUN.
[ ] Make smallest safe change.
[ ] Update docs/registers.
[ ] Run tests again.
[ ] Generate reports.
[ ] Repackage with matching folder/zip name.
[ ] Provide final package report.

This SOP is what turns a pile of AI-generated code into a maintainable engineering project.

Appendix

Lessona Learned
