# UniversalDAQ / uDAQ

UniversalDAQ, or **uDAQ**, is a device-agnostic data acquisition, signal mapping, diagnostics, historian, and control-workbench project.

The long-term goal is to build a flexible DAQ/control platform that can discover devices, map raw device I/O into canonical signals, visualize and review data, author logic safely, export diagnostics, and eventually support controlled outputs through explicit safety, authorization, and audit boundaries.

This repository is being developed through controlled sprint baselines. Each sprint preserves the active implementation, historical context, governance records, validation artifacts, and known limitations so future work can continue without losing design intent.

---

## Current Baseline

Current baseline:

`20260515_02_mapping-r2`

Formal package identity:

`UDQ-PKG-20260515-02-MAPPING-R02`

Sprint title:

`Sprint 1 — Sandbox Mapping Mutation Proof, R2 Hotfix`

This version establishes a controlled sandbox-only mapping workflow:

- mapping changes can be applied to sandbox state
- sandbox changes can be diffed
- sandbox changes can be rolled back
- diagnostic reports can be generated
- the visible shell includes a `Testing` menu
- the R2 hotfix repairs visible-shell startup and wiring regressions from the first Sprint 1 package

This version does **not** implement live hardware mutation or real output writes.

---

## Current Capability Status

Implemented in this baseline:

- device-agnostic core package structure
- active/historical package lanes
- governance and release documentation
- sprint sequence register
- sandbox mapping apply model
- mapping diff reporting
- mapping rollback proof
- visible operator shell foundation
- GUI-accessible `Testing` menu
- diagnostic launcher
- manual test checklist
- package validation tools
- simulated/demo paths that do not require hardware
- support-pack isolation pattern for LabJack, Arduino, and Raspberry Pi

Explicitly not implemented yet:

- live mapping apply
- live output writes
- production command authority
- production historian
- full graphing/review workbench
- full Logic Designer deployment
- Modbus support pack
- remote review mode
- installer/release-candidate packaging

---

## Repository Structure

The repository root is expected to contain:

```text
ACTIVE/
HISTORICAL/
ROOT_PACKAGE_INDEX.md
README.md
.gitattributes
````

### `ACTIVE/`

Current active package contents: implementation, current documentation, tests, tools, release notes, diagnostics, and validation artifacts.

Important entry points:

```text
ACTIVE/README_START_HERE.md
ACTIVE/PACKAGE_MANIFEST.md
ACTIVE/WORKPLAN_CURRENT_RUN.md
ACTIVE/KNOWN_LIMITATIONS.md
ACTIVE/ACCEPTANCE_TEST_PLAN.md
ACTIVE/RUN_UDAQ.bat
ACTIVE/RUN_DIAGNOSTICS.bat
```

### `HISTORICAL/`

Preserved historical packages, retired references, old audits, reconciliation ledgers, and external reference material.

Historical files are retained for traceability but are not the active implementation authority.

---

## Quick Start on Windows

From the repository root:

```bat
cd ACTIVE
RUN_UDAQ.bat
```

This launches the visible operator shell in safe demo/sandbox mode.

No hardware is required for the current sandbox workflow.

To run diagnostics:

```bat
cd ACTIVE
RUN_DIAGNOSTICS.bat
```

Diagnostic outputs are written under:

```text
ACTIVE/diagnostics/
ACTIVE/audit_reports/testing/
```

---

## Python Setup

From inside `ACTIVE/`:

```bat
py -m pip install -e ".[ui,dev]"
```

For UI-only use:

```bat
py -m pip install -e ".[ui]"
```

Core optional UI dependencies include:

```text
PySide6
pyqtgraph
```

---

## Testing

The current package provides both GUI-accessible and command-line test paths.

Launch the app:

```bat
cd ACTIVE
RUN_UDAQ.bat
```

Then use the top menu:

```text
Testing
  Run Smoke Test
  Run Mapping Sandbox Demo
  Run Apply/Rollback Test
  Run Diff Report Test
  Run Diagnostic Bundle Export
  Run Visible Shell Wiring Audit
  Open Manual Test Checklist
  Open Latest Report Folder
```

Manual checklist:

```text
ACTIVE/docs/testing/20260515_02_manual-test-checklist.md
```

Focused pytest examples from `ACTIVE/`:

```bat
py -m pytest tests/unit/test_mapping_sandbox_state.py -q
py -m pytest tests/unit/test_mapping_sandbox_diff.py -q
py -m pytest tests/contract/test_mapping_apply_sandbox_boundary.py -q
py -m pytest tests/contract/test_mapping_apply_rollback.py -q
py -m pytest tests/contract/test_contract_visible_shell_wiring_hotfix.py -q
```

---

## Safety Posture

uDAQ is being developed with strict separation between:

```text
requested state
applied state
observed state
```

The current baseline is sandbox-only for mapping mutation.

Important current boundary:

```text
Sandbox mapping apply is allowed.
Live mapping apply is not yet implemented.
Hardware output writes are not yet implemented.
```

Do not add live hardware mutation, live output writes, or automatic control behavior without routing the work through the planned runtime authority, command arbitration, authorization, audit, and safe-state layers.

---

## Support-Pack Philosophy

The UniversalDAQ core must remain device-agnostic.

Vendor or platform details belong in optional support packs, not in the universal core.

Current support-pack surfaces include:

```text
ACTIVE/src/universaldaq_labjack/
ACTIVE/src/universaldaq_arduino/
ACTIVE/src/universaldaq_rpi/
```

The core package should not directly depend on LabJack, Arduino, Raspberry Pi, Modbus, or other device-specific libraries.

Device-specific functionality should be isolated behind adapter contracts and capability declarations.

---

## Development Roadmap

The controlled sprint roadmap is maintained in:

```text
ACTIVE/docs/active/UDQ-ROADMAP-SPEC-001__Completed_Product_Roadmap_and_Sprint_Sequence__r0__ACTIVE.md
ACTIVE/registries/active/universalDAQ_sprint_sequence_register_r0.json
ACTIVE/registries/active/universalDAQ_sprint_sequence_register_r0.csv
```

Immediate next planned sprint:

`20260515_03_state`

Purpose:

`Authoritative Runtime State Model`

The next sprint is intended to establish one canonical runtime truth model for devices, points, signals, mappings, variables, logic, and UI projections.

---

## Contributing

Contributions should preserve the controlled package discipline.

Before changing code, read:

```text
ACTIVE/README_START_HERE.md
ACTIVE/WORKPLAN_CURRENT_RUN.md
ACTIVE/KNOWN_LIMITATIONS.md
ACTIVE/ACCEPTANCE_TEST_PLAN.md
ACTIVE/docs/handbook/NEXT_ACTIONS.md
ACTIVE/docs/handbook/TESTS_AND_TOOLS.md
```

For larger work, also read:

```text
ACTIVE/docs/active/UDQ-SPRINT-SOP-001__Sprint_Planning_Execution_and_Closeout_Process__r0__ACTIVE.md
ACTIVE/docs/active/UDQ-ROADMAP-SPEC-001__Completed_Product_Roadmap_and_Sprint_Sequence__r0__ACTIVE.md
```

### Pull Request Expectations

A pull request should include:

* summary of what changed
* files or subsystems touched
* tests run
* screenshots if UI changed
* diagnostic output if relevant
* known limitations
* confirmation that no live hardware mutation was added unless explicitly intended

### Preserve Existing Functionality

Avoid:

* deleting existing panels, menu items, tests, or docs without explanation
* replacing real behavior with stubs
* hiding errors instead of diagnosing them
* moving documents without updating registries
* adding vendor-specific imports to universal core modules
* changing public APIs without a compatibility note

### Required Validation for UI Changes

Any UI change should include at least:

```text
visible shell construction test
Testing menu wiring test
workspace tab-cycle test
diagnostic export test
manual launch check through RUN_UDAQ.bat
```

### Required Validation for Mapping/State Changes

Any mapping or state change should prove:

```text
sandbox state and live state remain separate
diffs are accurate
rollback restores expected state
failure modes are explicit
no hardware writes occur
```

### Required Validation for Hardware/Support-Pack Changes

Any hardware or support-pack change should prove:

```text
core imports without the optional hardware library
missing hardware degrades gracefully
device-specific code remains outside universal core
diagnostics explain missing dependencies
no unsafe output path is introduced
```

---

## Packaging Convention

Package artifacts should use short names:

```text
yyyymmdd_00_short.zip
```

Examples:

```text
20260515_02_mapping.zip
20260515_02_mapping-r2.zip
20260515_03_state.zip
```

Detailed descriptions belong inside release notes and package docs, not in the zip filename.

---

## Current Warning

This project is under active development.

The current baseline is suitable for sandbox/demo testing, architecture review, diagnostics validation, and continued implementation.

It is not yet suitable for unattended control, safety-critical operation, production hardware actuation, or live process control.

```
```
