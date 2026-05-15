---
document_id: DOC-050
title: "SOP: Monolithic Prototype Code"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-050
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# SOP: Monolithic Prototype Code

## 0. Purpose

A monolithic Python prototype is an intentionally temporary engineering artifact.

It exists to let us move quickly while the concept, workflow, data model, UI behavior, hardware behavior, file handling, or architecture is still being discovered. The goal is not to create the final structure immediately. The goal is to create one runnable, understandable, testable file that can prove whether the idea works in practice before we commit to a formal package structure.

This approach is especially useful for the kinds of projects we often build:

- desktop GUI tools;
- engineering utilities;
- data acquisition systems;
- hardware-control programs;
- simulation and visualization tools;
- file scanners and cataloging tools;
- local/offline utilities;
- legacy-system tools;
- Raspberry Pi, LabJack, Arduino, ESP32, serial, VISA, or instrument-control programs;
- workflow prototypes where the correct user interaction is not yet known.

The monolithic prototype is not treated as disposable scratch code. It is treated as a controlled staging artifact.

That means it should be:

- runnable;
- readable;
- sectioned internally;
- diagnostic-friendly;
- safe to test;
- clear about assumptions;
- clear about known limitations;
- designed for later extraction;
- resistant to feature loss during future refactoring.

The prototype should answer practical questions such as:

- Does the workflow make sense when used directly?
- Does the UI layout support the real task?
- Does the data model survive realistic use?
- Does the file handling work on the target machine?
- Does the hardware behave as expected?
- Does the logging capture useful evidence?
- Does the user receive enough feedback?
- Does the performance seem acceptable?
- Does the concept deserve formalization?

The monolithic prototype is successful when it teaches us enough to either:

1. discard the idea;
2. revise the concept;
3. continue prototyping;
4. freeze the feature set;
5. split the code into a formal package.

It is not successful merely because it runs once.

A good monolithic prototype should become the “golden behavioral baseline” for later modularization. Once the prototype proves the workflow, its features, command-line flags, settings, data fields, UI controls, diagnostic outputs, and user-visible behaviors should be inventoried before any refactor begins.

## 1. Philosophy

The monolithic prototype is a deliberate tradeoff.

It accepts short-term structural debt in exchange for fast discovery, lower coordination overhead, and easier whole-system experimentation.

During early development, separating everything into modules too soon can create false precision. The real boundaries are often not known yet. We may not know which parts of the UI will survive, which data fields matter, what hardware behavior is reliable, what workflows the user will actually use, or where the performance bottlenecks are.

A monolithic file lets us explore those questions with minimal ceremony.

However, the file must be written with future extraction in mind. The goal is not to make a tangled script. The goal is to create a single-file prototype with visible internal architecture.

The file should behave like a modular project compressed into one file.

That means:

- imports are centralized;
- constants are centralized;
- paths and settings are grouped;
- data models are grouped;
- storage is grouped;
- scanning/parsing/import logic is grouped;
- business actions are grouped;
- UI or rendering code is grouped;
- diagnostics and smoke tests are grouped;
- startup and shutdown are explicit;
- prototype debt is recorded;
- extraction targets are identified.

The prototype should make future refactoring easier, not harder.

A bad monolithic prototype hides everything in one uncontrolled flow.

A good monolithic prototype has clear section boundaries that later become module boundaries.

## 2. Methodology

The monolithic-code methodology is:

1. Start with the concept and workflows.
2. Build one runnable file that exercises the core idea.
3. Keep the code internally sectioned from the beginning.
4. Add diagnostics early, not after the project breaks.
5. Preserve settings, state, and data deliberately.
6. Avoid silent feature removal during iteration.
7. Record known prototype debt inside the file.
8. Add smoke-test and diagnostic modes as soon as practical.
9. Use the prototype to discover the real feature set.
10. Freeze the working behavior before refactoring.
11. Create a feature inventory.
12. Define module boundaries.
13. Extract in phases only after acceptance tests exist.

The prototype should always be able to produce useful evidence.

At minimum, serious prototypes should eventually support:

- normal run mode;
- `--version`;
- `--smoke-test`;
- `--diagnostics`;
- safe-mode behavior where relevant;
- a copy/pasteable diagnostic report;
- explicit startup and shutdown behavior;
- readable error messages;
- basic file read/write validation;
- import/dependency checks;
- runtime path reporting.

For hardware or control software, the prototype must also include safe-state thinking from the beginning:

- start safe;
- fail safe;
- do not auto-enable dangerous outputs;
- expose manual safe-state behavior;
- log command state clearly;
- handle disconnects and exceptions explicitly.

For GUI software, the prototype should include basic quality-of-life expectations early:

- sensible default window size;
- resizable layout where practical;
- scrollable controls if needed;
- persistent settings if practical;
- clear user feedback;
- logs or diagnostics reachable by the user;
- graceful shutdown.

The prototype does not need to be architecturally final, but it must not be careless.

## 3. When to Use a Monolithic Prototype

Use a monolithic Python prototype when:

- the concept is still evolving;
- the user workflow is not fully proven;
- the data model is not stable;
- the UI layout needs hands-on testing;
- hardware behavior needs direct experimentation;
- file formats or external data are uncertain;
- the target environment is unusual, old, offline, embedded, or constrained;
- speed of iteration matters more than clean packaging;
- the project needs a working behavioral baseline before formalization;
- the cost of premature architecture is higher than the cost of temporary monolithic debt.

A monolithic prototype is appropriate when we are still asking:

- What should this tool actually do?
- What should the user see first?
- What controls are needed?
- What data needs to persist?
- What edge cases matter?
- What breaks on the target machine?
- What diagnostics will we need when testing remotely?
- What parts of the program naturally belong together?
- What parts should eventually become separate modules?

The prototype stage is where we learn the real shape of the project.

## 4. When Not to Use a Monolithic Prototype

Do not use a monolithic prototype as the primary structure when:

- the requirements are already stable;
- the module boundaries are already known;
- the codebase already has a working professional package structure;
- multiple developers or agents need to work independently in parallel;
- the program is already safety-critical and lacks adequate safeguards;
- the prototype has already proven the feature set;
- the next task is refactoring, packaging, testing, or release hardening;
- the monolithic file has become too large to audit safely.

Once the prototype has proven the workflow, continuing to add features to the monolith becomes risky.

At that point, the correct next step is not “keep coding.” The correct next step is:

1. freeze the working prototype;
2. record the current feature inventory;
3. identify public interfaces;
4. write or update acceptance tests;
5. define module boundaries;
6. create a package structure;
7. extract the lowest-risk layers first;
8. verify no feature loss after each extraction.

## 5. How the Monolithic Prototype Prepares for Formal Structure

A monolithic prototype should be written so that its internal sections map naturally to future files.

Recommended internal sections:

1. Imports and compatibility
2. Constants and version information
3. Paths, settings, and logging
4. Data model and defaults
5. Storage / load / save
6. Scanning / import / parsing
7. Business logic / actions
8. UI / view rendering
9. Diagnostics / smoke tests
10. Main application / entry point

These sections are not just visual dividers. They are future extraction boundaries.

Typical future extraction map:

| Monolithic Section | Future Module Target |
|---|---|
| Imports and compatibility | `project/compat.py` |
| Constants and version info | `project/constants.py` |
| Paths/settings/logging | `project/paths.py`, `project/settings.py`, `project/logging.py` |
| Data model/defaults | `project/model.py` or `project/schema.py` |
| Storage/load/save | `project/storage.py` |
| Scanning/import/parsing | `project/scanner.py`, `project/parser.py`, or `project/importer.py` |
| Business logic/actions | `project/actions.py` or `project/services.py` |
| UI/view rendering | `project/ui/`, `project/views/`, or `project/gui/` |
| Diagnostics/smoke tests | `project/diagnostics.py`, `tools/diagnostic_harness.py` |
| Main application/entry point | `main.py` or package launcher |

This lets the prototype become the behavioral seed of the formal project instead of becoming a dead-end script.

## 6. Definition of Done for a Monolithic Prototype

A monolithic prototype is ready for formalization when an independent reviewer can answer:

- What does the prototype do?
- How do you run it?
- What workflows does it support?
- What data does it create or modify?
- What settings does it persist?
- What user-visible features exist?
- What diagnostics are available?
- What known bugs or limitations remain?
- What behavior must not be lost?
- What sections should become modules?
- What tests prove the current behavior?
- What risks exist if it is refactored?

If the reviewer needs chat history to answer those questions, the prototype is not ready for formalization.

## 7. Core Rule

A monolithic prototype is allowed.

An unstructured monolithic prototype is not.

The prototype should be fast to change now, but disciplined enough that it can become a professional package later without losing features, rewriting from memory, or relying on undocumented assumptions.
