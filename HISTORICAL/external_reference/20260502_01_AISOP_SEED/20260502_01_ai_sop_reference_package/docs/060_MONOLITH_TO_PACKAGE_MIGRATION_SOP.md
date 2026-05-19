---
document_id: DOC-060
title: "SOP: Monolith-to-Package Migration"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-060
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# SOP: Monolith-to-Package Migration

I’d add this as a new section between Preliminary Code and ZIP Workflow, because it formalizes the missing handoff step: turning a working monolithic prototype into a professional package without losing behavior, scrambling architecture, or pretending the first extraction is already the final design.
This fits the existing AISOP rules: freeze the baseline, identify the current feature set, define module boundaries, avoid broad rewrites, extract lowest-risk layers first, and run smoke tests/diagnostics after each phase.
# SOP: Transferring a Monolithic Prototype into a Formal Zip Package

## 0. Purpose

This SOP defines the formal process for converting a working monolithic prototype into a professional zipped software package.

The purpose is to prevent the common failure mode where a useful monolithic prototype is broken apart too quickly, producing a package that looks more professional but quietly loses features, changes behavior, breaks diagnostics, or becomes harder to understand.

The transfer from monolithic code to formal package is not a simple file-splitting task.

It is a controlled migration.

The goal is to preserve the prototype’s proven behavior while gradually creating:

- a clean package structure;
- documented requirements;
- a feature inventory;
- module boundaries;
- public interface definitions;
- diagnostic tools;
- smoke tests;
- acceptance tests;
- changelog records;
- risk and debt registers;
- a repeatable handoff process.

The monolithic prototype remains the behavioral reference until the modular package proves equivalent.

## 1. Core Philosophy

The monolithic prototype is the discovery artifact.

The formal zip package is the maintainable delivery artifact.

The transfer process exists between those two stages.

During prototyping, we accept temporary structural debt so we can discover workflows, data needs, UI behavior, hardware behavior, and user expectations quickly.

During package formalization, we stop adding uncontrolled prototype features and start protecting what has been learned.

The job is not to make the code “look modular” as fast as possible.

The job is to preserve behavior while making structure explicit.

A successful transfer should answer:

- What exactly worked in the monolith?
- What features must be preserved?
- What public interfaces already exist?
- What data must remain compatible?
- What startup/shutdown behavior must remain unchanged?
- What diagnostics must continue to work?
- What modules should eventually exist?
- What should be extracted first?
- What should not be touched yet?
- How do we prove no feature loss occurred?

If those answers are unclear, extraction should not begin.

## 2. Transfer Stages Overview

The transfer from monolithic prototype to formal package happens in stages:

1. Freeze the monolithic baseline.
2. Create a transfer workplan.
3. Inventory the current behavior.
4. Identify public interfaces.
5. Define the target package skeleton.
6. Split planning documents before splitting code.
7. Add package-level diagnostics and smoke tests.
8. Create compatibility shims.
9. Extract the lowest-risk support layers.
10. Validate behavior after each extraction.
11. Continue staged extraction.
12. Retire the monolith only after equivalence is proven.
13. Package, audit, and hand off.

Do not skip directly from “working monolith” to “fully modular app.”

That jump is where feature loss and interface drift usually happen.

## 3. Transfer Entry Criteria

Do not begin formal transfer until the prototype satisfies at least the minimum baseline conditions.

Required:

- The monolithic prototype runs.
- The main entry point is known.
- The target runtime is known.
- The target OS/environment is known.
- The main workflows are understood.
- The important user-visible features are identifiable.
- The current data files or persistence behavior are understood.
- Known bugs and limitations are recorded.
- The prototype has either a smoke test, diagnostic mode, or manual test procedure.
- A rollback copy of the monolithic prototype exists.

Preferred:

- The prototype supports `--version`.
- The prototype supports `--smoke-test`.
- The prototype supports `--diagnostics`.
- The prototype writes a copy/pasteable diagnostic report.
- The prototype has a sectioned internal structure.
- The prototype has an internal prototype debt register.
- The prototype has an extraction map.

If the monolith cannot be run or tested, treat the transfer as a recovery/refactor project, not a normal formalization.

## 4. Phase 0 — Freeze the Monolithic Baseline

Before creating the formal package, freeze the working monolithic code.

Actions:

1. Copy the working monolithic file unchanged.
2. Give it a clear frozen-baseline name.
3. Record the date and version.
4. Save known run instructions.
5. Save known test instructions.
6. Save screenshots or diagnostic output if useful.
7. Record the environment where it last worked.
8. Do not edit the frozen baseline.

Recommended folder:

```text
prototype/
├── frozen_baseline/
│   ├── yyyymmdd_00_project_monolithic_baseline.py
│   ├── BASELINE_RUN_NOTES.md
│   ├── BASELINE_TEST_NOTES.md
│   └── BASELINE_DIAGNOSTIC_REPORT.txt

The frozen baseline is the behavioral reference.
If the formal package later behaves differently, the question becomes:
Was that difference intentional?
If not, it is a regression.
5. Phase 1 — Create the Transfer Workplan
Before moving code, create:
docs/005_MONOLITH_TO_PACKAGE_TRANSFER_PLAN.md

This document defines the transfer scope.
Required contents:
# 005_MONOLITH_TO_PACKAGE_TRANSFER_PLAN

## 0. Document Control
Project:
Package/run name:
Date:
Author/reviewer:
Source monolithic file:
Frozen baseline path:
Target package name:
Transfer status:

## 1. Purpose of This Transfer
What are we trying to accomplish in this package/run?

## 2. Source Baseline
Monolithic file:
Version/date:
Known runnable command:
Known test command:
Known environment:
Known limitations:

## 3. Target Package
Zip/package name:
Internal folder name:
Primary entry point:
Source package folder:
Docs folder:
Tools folder:
Tests folder:

## 4. Scope
This transfer will change:
This transfer will not change:
Files expected to change:
Files explicitly not to change:
Behavior expected to change:
Behavior expected unchanged:

## 5. Transfer Strategy
[ ] Documentation-only transfer
[ ] Package skeleton only
[ ] Diagnostics-first transfer
[ ] Compatibility/helper extraction
[ ] Settings/path/logging extraction
[ ] Data/storage extraction
[ ] Business logic extraction
[ ] UI extraction
[ ] Full modularization

## 6. Acceptance Gate
What must pass before this transfer is accepted?

## 7. Rollback Plan
How do we return to the frozen monolith if the package fails?

## 8. Known Risks
List risks or reference risk register.

## 9. Next Step After This Transfer
What is the smallest safe next move?

Rule:
If this transfer plan cannot be written clearly, the transfer is not ready.
6. Phase 2 — Create the Current Feature Inventory
Before moving functions, create or update:
docs/020_CURRENT_FEATURE_INVENTORY.md

This is one of the most important anti-feature-loss tools.
Format:
FEATURE-001
Name:
Category:
Current behavior:
Where implemented in monolith:
User-visible? Yes/No
Data-visible? Yes/No
CLI/API/UI surface:
Required settings/state:
Required files:
Known dependencies:
Must preserve? Yes/No
Acceptance check:
Notes:

Feature categories:
* startup/shutdown;
* CLI flags;
* GUI controls;
* menus;
* settings;
* persistence;
* file scanning;
* device communication;
* plotting/visualization;
* logging;
* diagnostics;
* exports;
* keyboard shortcuts;
* safety behavior;
* error handling;
* user workflows.
Rules:
* Do not rely on memory.
* Inspect the actual monolithic file.
* Include small features.
* Include diagnostics.
* Include hidden but important behaviors.
* Include settings and persistence behavior.
* Include safe-state behavior if hardware is involved.
* Include known bugs separately from intended features.
A feature not listed here is at risk of being lost.
7. Phase 3 — Identify Public Interfaces Before Extraction
Create:
docs/025_PUBLIC_INTERFACE_FREEZE.md

This file records every surface that other code, users, saved files, launchers, or tests may depend on.
Interfaces include:
* main script name;
* command-line arguments;
* config keys;
* JSON/CSV/database schema fields;
* runtime folder names;
* log/report filenames;
* GUI menu names;
* GUI button/action names;
* keyboard shortcuts;
* route URLs;
* API commands;
* hardware command names;
* device channel naming;
* importable functions/classes already used elsewhere.
Format:
IFACE-001
Type:
Name/path/key:
Current behavior:
Inputs:
Outputs:
Side effects:
Used by:
Compatibility requirement:
Can change during this transfer? Yes/No
If yes, migration/shim plan:
Acceptance check:

Rule:
Do not rename public interfaces during the first package transfer unless the change is explicitly approved and a compatibility shim is provided.
8. Phase 4 — Create the Target Package Skeleton
Create the formal folder structure before moving real logic.
Recommended initial structure:
yyyymmdd_00_description-of-run/
├── README_START_HERE.md
├── RUN_INSTRUCTIONS.md
├── TEST_INSTRUCTIONS.md
├── CHANGELOG.md
├── KNOWN_LIMITATIONS.md
│
├── main.py
│
├── project_name/
│   ├── __init__.py
│   ├── constants.py
│   ├── compat.py
│   ├── paths.py
│   ├── settings.py
│   ├── logging_utils.py
│   ├── diagnostics.py
│   └── app.py
│
├── prototype/
│   └── frozen_baseline/
│
├── docs/
│   ├── 000_MASTER_PROJECT_PLAN.md
│   ├── 005_MONOLITH_TO_PACKAGE_TRANSFER_PLAN.md
│   ├── 010_PRODUCT_REQUIREMENTS.md
│   ├── 020_CURRENT_FEATURE_INVENTORY.md
│   ├── 025_PUBLIC_INTERFACE_FREEZE.md
│   ├── 030_FOLDER_STRUCTURE_SPEC.md
│   ├── 040_ARCHITECTURE_SPEC.md
│   ├── 050_MODULE_BOUNDARY_SPEC.md
│   ├── 060_DATA_SCHEMA_SPEC.md
│   ├── 070_UI_LAYOUT_SPEC.md
│   ├── 080_ACCEPTANCE_TEST_PLAN.md
│   ├── 090_DIAGNOSTICS_SPEC.md
│   ├── 100_RISK_REGISTER.md
│   ├── 110_TECHNICAL_DEBT_REGISTER.md
│   ├── 120_DECISION_LOG.md
│   ├── 130_OPEN_QUESTIONS.md
│   └── 140_REFACTOR_SEQUENCE_PLAN.md
│
├── tools/
│   ├── diagnostic_harness.py
│   ├── package_smoke_test.py
│   ├── structure_audit.py
│   ├── dependency_audit.py
│   └── feature_inventory_check.py
│
├── tests/
│   └── README_TESTS.md
│
├── test_reports/
│   └── README_TEST_REPORTS.md
│
├── examples/
│   └── README_EXAMPLES.md
│
└── runtime_data/
    └── README_RUNTIME_DATA.md

For small projects, this can be simplified, but the package must still include:
* README;
* run instructions;
* test instructions;
* changelog;
* feature inventory;
* risk register;
* technical debt register;
* diagnostic harness;
* smoke test;
* frozen monolithic baseline.
9. Phase 5 — Split Documentation Before Splitting Code
Before extracting code, split or create the key planning documents.
Required minimum:
docs/010_PRODUCT_REQUIREMENTS.md
docs/020_CURRENT_FEATURE_INVENTORY.md
docs/025_PUBLIC_INTERFACE_FREEZE.md
docs/030_FOLDER_STRUCTURE_SPEC.md
docs/040_ARCHITECTURE_SPEC.md
docs/050_MODULE_BOUNDARY_SPEC.md
docs/080_ACCEPTANCE_TEST_PLAN.md
docs/090_DIAGNOSTICS_SPEC.md
docs/100_RISK_REGISTER.md
docs/110_TECHNICAL_DEBT_REGISTER.md
docs/120_DECISION_LOG.md
docs/140_REFACTOR_SEQUENCE_PLAN.md

The documentation does not need to be perfect, but it must be sufficient to prevent blind extraction.
Rules:
* Mark current behavior separately from planned behavior.
* Do not document aspirational features as if they already exist.
* Record unknowns explicitly.
* Use IDs for requirements, features, risks, debts, decisions, and acceptance tests.
* Keep the frozen monolith as the evidence source.
10. Phase 6 — Define Module Boundaries
Create or update:
docs/050_MODULE_BOUNDARY_SPEC.md

Format:
MODULE-001
Name:
Future file:
Purpose:
Owns:
Does not own:
Public functions/classes:
Depends on:
Used by:
Extract from monolith section:
Extraction phase:
Risk:
Acceptance test:
Status:

Typical module boundaries:
compat.py
Owns:
- Python-version compatibility
- text/bytes helpers
- path encoding helpers
Does not own:
- app settings
- UI behavior
- business logic

constants.py
Owns:
- app name/version
- schema version
- allowed status strings
- default filenames
Does not own:
- mutable settings
- user state

paths.py
Owns:
- package root detection
- runtime folder paths
- config path
- log/report paths
Does not own:
- JSON read/write
- business rules

settings.py
Owns:
- default settings
- load/save settings
- settings migration
Does not own:
- UI rendering
- hardware commands

logging_utils.py
Owns:
- log formatting
- log file writing
- exception logging
Does not own:
- diagnostics report formatting

model.py / schema.py
Owns:
- default data objects
- schema versions
- migrations
Does not own:
- file scanning
- UI updates

storage.py
Owns:
- load/save
- backup
- atomic writes
Does not own:
- user actions
- scanning policy

scanner.py / importer.py
Owns:
- discovering files/devices/data inputs
- parsing external data
- returning scan summaries
Does not own:
- rendering
- direct UI mutation

actions.py / services.py
Owns:
- user actions
- business rules
- controlled mutation
Does not own:
- low-level file paths
- GUI widget layout

ui/ or gui/
Owns:
- visual layout
- user controls
- event binding
Does not own:
- direct storage internals
- raw hardware protocol code

diagnostics.py
Owns:
- diagnostic collection
- report formatting
- environment checks
Does not own:
- app business logic except read-only checks

main.py
Owns:
- argument parsing
- startup order
- top-level exception handling
Does not own:
- business logic
- UI internals

Rule:
If a module’s responsibilities cannot be stated clearly, do not extract it yet.
11. Phase 7 — Build Package Diagnostics Before Major Extraction
Before moving core logic, create package-level tools:
tools/structure_audit.py
tools/package_smoke_test.py
tools/diagnostic_harness.py
tools/dependency_audit.py

Minimum checks:
Structure audit:
* required files exist;
* required folders exist;
* entry point exists;
* docs exist;
* tools exist;
* prototype baseline exists;
* no obvious accidental runtime/private files included;
* package name matches internal folder name where applicable.
Smoke test:
* imports package;
* imports main modules;
* runs get_app_info();
* checks version string;
* checks runtime folders can be resolved;
* performs temp read/write test;
* verifies diagnostics can be generated;
* does not touch real user data.
Diagnostic harness:
* Python version;
* OS/platform;
* working directory;
* package root;
* expected files/folders;
* import checks;
* config paths;
* data paths;
* dependency availability;
* GUI/display assumptions if relevant;
* file read/write test;
* representative function checks;
* traceback capture;
* pass/fail summary.
Dependency audit:
* imported modules;
* standard-library vs external dependencies;
* missing optional dependencies;
* target-runtime compatibility issues;
* forbidden dependency warnings.
Rule:
Diagnostics should be able to fail informatively before the app fails mysteriously.
12. Phase 8 — Create a Compatibility Shim Layer
The first code extraction should usually create compatibility shims, not move business logic.
A shim layer lets old call paths survive while new modules are introduced.
Example:
# Old monolith-style function preserved in app.py
def load_settings():
    from project_name.settings import load_settings as _load_settings
    return _load_settings()

Or:
# project_name/compat_api.py
# Temporary bridge for old names used by early package code.
from project_name.settings import load_settings, save_settings
from project_name.paths import get_appdata_dir, get_config_path

Shim rules:
* Mark shims as temporary.
* Record them in the technical debt register.
* Do not remove shims until callers are updated and tests prove equivalence.
* Do not use shims to hide uncontrolled architecture forever.
13. Phase 9 — Extraction Order
Use this extraction order unless the project has a specific reason not to.
Phase 9.1 — Constants and Metadata
Extract:
constants.py
__init__.py

Move:
* app name;
* version;
* phase;
* schema version;
* allowed status strings;
* default filenames.
Acceptance:
* package imports;
* version reports correctly;
* monolith baseline remains unchanged;
* no behavior change.
Phase 9.2 — Compatibility Helpers
Extract:
compat.py

Move:
* text/bytes helpers;
* safe path helpers;
* Python-version checks;
* platform compatibility helpers.
Acceptance:
* compatibility smoke test passes;
* weird filename/path test passes where relevant;
* no user-facing behavior changes.
Phase 9.3 — Paths, Settings, and Logging
Extract:
paths.py
settings.py
logging_utils.py

Move:
* package root detection;
* runtime data path;
* config path;
* settings defaults;
* load/save settings;
* log writing.
Acceptance:
* settings still load/save;
* old settings migrate or remain readable;
* logs still write;
* diagnostic report shows correct paths;
* no data loss.
Phase 9.4 — Diagnostics
Extract:
diagnostics.py
tools/diagnostic_harness.py
tools/package_smoke_test.py

Move:
* diagnostic collection;
* report formatting;
* smoke test helpers.
Acceptance:
* diagnostic harness runs from package root;
* report is copy/pasteable;
* failures include tracebacks;
* no real user data required.
Phase 9.5 — Data Model and Storage
Extract:
model.py
schema.py
storage.py

Move:
* object factories;
* schema defaults;
* load/save data;
* backup behavior;
* migration behavior.
Acceptance:
* existing data opens;
* unknown fields are preserved where practical;
* backups are created before migration;
* corrupt/missing data failure is handled clearly;
* feature inventory data-related checks pass.
Phase 9.6 — Scanning / Import / Parsing
Extract:
scanner.py
parser.py
importer.py

Move:
* directory scanning;
* file parsing;
* device discovery;
* external input import;
* structured scan summaries.
Acceptance:
* scan result counts match baseline;
* missing files/devices are handled as before;
* scanner does not directly render UI;
* scanner does not delete user records unless explicitly intended.
Phase 9.7 — Business Logic / Actions
Extract:
actions.py
services.py
controllers.py

Move:
* mark/update actions;
* controlled data mutation;
* workflow transitions;
* command routing;
* safety-state actions.
Acceptance:
* user-visible workflows still work;
* action results are explicit;
* UI does not directly mutate storage internals where avoidable;
* hardware/control actions remain safe.
Phase 9.8 — UI / View / GUI
Extract:
ui/
views/
gui/

Move:
* layout;
* menus;
* buttons;
* panels;
* rendering;
* event handlers.
Acceptance:
* all listed UI controls still exist;
* default window behavior is preserved or intentionally improved;
* settings persistence still works;
* diagnostics/logs remain reachable;
* no important content is pushed out of view unintentionally.
Phase 9.9 — Specialized Engines
Extract as needed:
plotting.py
visualization/
simulation/
devices/
adapters/
protocols/

Move:
* plotting engines;
* simulation logic;
* hardware adapters;
* protocol handlers;
* device-specific code.
Acceptance:
* representative real or simulated data works;
* hardware starts safe and fails safe;
* disconnect behavior is logged;
* plots/exports match baseline expectations.
Phase 9.10 — Thin Entrypoint
Finalize:
main.py

The entry point should only:
* parse CLI args;
* initialize paths/settings/logging;
* run safety checks;
* start app;
* catch top-level exceptions;
* call safe shutdown if needed;
* return exit code.
Acceptance:
* package runs from documented command;
* launchers still work;
* diagnostics still work;
* smoke test passes;
* feature inventory check passes.
14. Phase Gate After Every Extraction
After each extraction phase, stop and validate.
Required checks:
[ ] App/package imports.
[ ] Main entry point still runs.
[ ] Frozen baseline remains unchanged.
[ ] Smoke test passes.
[ ] Diagnostic harness runs.
[ ] Structure audit passes or known issues are documented.
[ ] Feature inventory checked.
[ ] Public interfaces unchanged or shimmed.
[ ] Changelog updated.
[ ] Risk register updated.
[ ] Technical debt register updated.
[ ] No accidental runtime/private files included.
[ ] Rollback remains possible.

Do not continue to the next extraction phase until the current phase has passed or failures are explicitly accepted.
15. Feature Inventory Check
Create:
tools/feature_inventory_check.py

This tool can start simple.
It should eventually verify:
* expected files exist;
* expected CLI flags exist;
* expected config keys exist;
* expected report files can be generated;
* expected public functions/classes import;
* expected UI/action names are still present where checkable;
* expected data fields still exist;
* diagnostics still include required sections.
Manual checks are acceptable early, but they must be recorded.
Create report:
test_reports/feature_inventory_check_report.txt

Report format:
Feature inventory check
Timestamp:
Environment:
Package:
Baseline:
Features checked:
Features passed:
Features failed:
Features not automated:
Manual checks required:
Summary:

16. Changelog Requirements During Transfer
Every extraction phase must update:
CHANGELOG.md

Format:
## yyyymmdd_00_description-of-run

Purpose:

Source baseline:

Changed files:

Added files:

Removed files:

Behavior changes:
- None intended / list intentional changes

Non-behavioral changes:
- Example: moved constants into project_name/constants.py

Feature removals:
- None intended / list explicitly approved removals

Compatibility changes:
- None intended / list

Tests run:
- structure_audit.py: PASS/FAIL
- package_smoke_test.py: PASS/FAIL
- diagnostic_harness.py: PASS/FAIL
- feature_inventory_check.py: PASS/FAIL

Known limitations:

Risks introduced:

Risks reduced:

Debt added:

Debt resolved:

Next recommended step:

Bad changelog entry:
Refactored app.

Good changelog entry:
Moved path and settings helpers from the monolithic prototype into project_name/paths.py and project_name/settings.py.
Added compatibility shims so old calls still work.
No UI, scanner, storage schema, or business logic extraction performed.
Smoke test and diagnostic harness pass.
No intended feature removals.

17. Technical Debt Handling During Transfer
The monolith itself is debt, but not all debt should be fixed during transfer.
Create or update:
docs/110_TECHNICAL_DEBT_REGISTER.md

Debt categories:
* intentional monolith debt;
* temporary compatibility shims;
* duplicated logic during extraction;
* weak tests;
* unclear module ownership;
* legacy compatibility constraints;
* data migration risk;
* GUI layout debt;
* hardware safety debt;
* incomplete diagnostics;
* packaging cleanup.
Rule:
Do not fix unrelated debt while performing a narrow extraction.
Record it.
Fix it in a planned phase.
18. Risk Register During Transfer
Create or update:
docs/100_RISK_REGISTER.md

Common transfer risks:
RISK-TRANSFER-001
Title: Feature loss during extraction
Likelihood: High
Impact: High
Detection:
Feature inventory check, manual workflow test, smoke test.
Mitigation:
Freeze baseline, inventory features, extract in phases, compare behavior after each phase.
Fallback:
Restore frozen monolith or previous package.

RISK-TRANSFER-002
Title: Interface drift
Likelihood: Medium
Impact: High
Detection:
Public interface freeze review, CLI/config/schema checks.
Mitigation:
Use compatibility shims; avoid renaming during first transfer.
Fallback:
Reintroduce old interface wrapper.

RISK-TRANSFER-003
Title: Documentation claims exceed actual code
Likelihood: Medium
Impact: Medium
Detection:
Compare docs to code during package review.
Mitigation:
Label future/planned behavior clearly.
Fallback:
Correct docs before coding further.

RISK-TRANSFER-004
Title: Runtime data accidentally bundled
Likelihood: Medium
Impact: Medium/High
Detection:
Structure audit; manual package inspection.
Mitigation:
Exclude runtime_data unless intentionally included.
Fallback:
Repackage without private/generated data.

RISK-TRANSFER-005
Title: Hardware behavior changes during refactor
Likelihood: Medium
Impact: Critical
Detection:
Safe-state test, simulated hardware test, manual hardware acceptance.
Mitigation:
Extract hardware last unless safety layer is the specific task; preserve safe startup/shutdown.
Fallback:
Restore baseline hardware control path.

19. What Not To Do
Do not:
* split the monolith by guessing;
* rewrite the app from memory;
* delete the monolithic baseline;
* rename public interfaces casually;
* move UI and business logic at the same time;
* move storage and schema at the same time without backups/tests;
* modernize dependencies during structural transfer;
* fix unrelated bugs during extraction unless required;
* add major new features during transfer;
* claim equivalence without tests or diagnostics;
* trust documentation without checking code;
* bundle private runtime data by accident;
* remove compatibility shims before all callers are updated;
* extract high-risk GUI/device logic before low-risk support layers.
20. Transfer Acceptance Criteria
A monolithic-to-package transfer is accepted only when:
[ ] Frozen monolithic baseline exists.
[ ] Formal package structure exists.
[ ] Package and internal folder names follow convention.
[ ] README_START_HERE exists.
[ ] RUN_INSTRUCTIONS exists.
[ ] TEST_INSTRUCTIONS exists.
[ ] CHANGELOG exists.
[ ] Current feature inventory exists.
[ ] Public interface freeze exists.
[ ] Module boundary spec exists.
[ ] Risk register exists.
[ ] Technical debt register exists.
[ ] Diagnostic harness exists.
[ ] Smoke test exists.
[ ] Structure audit exists.
[ ] App/package imports successfully.
[ ] Main entry point runs.
[ ] Diagnostic report can be generated.
[ ] Smoke test passes or failures are documented.
[ ] Feature inventory was checked.
[ ] No unapproved feature removals occurred.
[ ] No unapproved public interface changes occurred.
[ ] Runtime/private files are excluded unless intentionally documented.
[ ] Known limitations are updated.
[ ] Next safe step is documented.

If any required item fails, the package can still be delivered as a partial transfer, but it must be labeled honestly as incomplete.
21. Formal Package Report After Transfer
Every transfer package should end with a report:
Package:
Internal folder:
Based on frozen monolith:
Transfer type:
Purpose:

Changed files:

Added files:

Removed files:

Behavior changes:
Feature removals:
Public interface changes:
Compatibility shims added:

Tests run:
Test results:

Diagnostics report:
Structure audit:
Feature inventory check:

Known limitations:

Risks:
Debt added:
Debt resolved:

Broad refactor performed? Yes/No

Rollback path:

Next recommended step:

22. When the Monolith Can Be Retired
Do not delete the monolithic prototype immediately after creating the package.
Retire it only when:
* the modular package runs;
* all core workflows are represented in tests or manual acceptance checks;
* feature inventory checks pass;
* diagnostics are package-native;
* public interfaces are stable;
* data migration behavior is known;
* the package has become the new golden baseline.
When retired, move it to:
prototype/archive/

Add a note:
This monolithic prototype was retained as the behavioral baseline during package formalization.
The formal package became authoritative on YYYY-MM-DD after acceptance checks passed.

23. Definition of Done
The transfer is complete when an independent reviewer can open the package and determine:
* what project this is;
* what monolithic file it came from;
* what behavior existed in the monolith;
* what features were preserved;
* what changed during transfer;
* what did not change;
* how to run the app;
* how to test the app;
* how to generate diagnostics;
* what risks remain;
* what debt remains;
* what module boundaries exist;
* what extraction phase comes next;
* how to roll back if needed.
If the reviewer needs chat history to understand the transfer, the transfer package is incomplete.
24. Core Rule
Do not treat formalization as cleanup.
Treat it as migration.
The monolithic prototype is evidence.
The package is the controlled deliverable.
The transfer process is what protects the work between them.
