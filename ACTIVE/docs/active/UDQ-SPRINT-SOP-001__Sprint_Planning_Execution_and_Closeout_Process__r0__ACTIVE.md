# Sprint Planning, Execution, and Closeout Process

**Controlled document**  
ID: UDQ-SPRINT-SOP-001  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture  
Authority: PRIMARY  
Source docs: UDQ-GOV-SOP-001, UDQ-GOV-SOP-002, UDQ-GOV-TPL-001, UDQ-PROOF-TPL-001, UDQ-ROADMAP-SPEC-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Purpose

This SOP defines how UniversalDAQ sprints are planned, executed, validated, documented, and closed out from Sprint Zero onward. It is intended to prevent feature loss, interface drift, stale documentation, uncontrolled scope expansion, and validator/tooling churn.

## Standing sprint inputs

Before each sprint begins, review the following surfaces in this order:

1. `docs/handbook/NEXT_ACTIONS.md`
2. `registries/active/universalDAQ_sprint_sequence_register_r0.json`
3. `docs/active/UDQ-ROADMAP-SPEC-001__Completed_Product_Roadmap_and_Sprint_Sequence__r0__ACTIVE.md`
4. `KNOWN_LIMITATIONS.md`
5. `docs/active/UDQ-GAP-RPT-001__Open_Implementation_Gaps__r11__WIP.md`
6. `docs/handbook/TESTS_AND_TOOLS.md`
7. affected subsystem specifications
8. current release notes and validation summaries

## Sprint planning requirements

Each sprint plan must define:

- package/run name using the `yyyymmdd_00_description` convention
- package ID
- objective
- preconditions
- explicit non-goals
- source surfaces that may be touched
- docs/registry surfaces that may be touched
- required tests and validators
- risks and mitigations
- acceptance criteria
- proof artifacts to produce
- downstream sprint(s) unlocked

## Execution rules

- Do not remove or alter existing features unless explicitly requested.
- Freeze public APIs early; if refactoring is required, add a compatibility shim rather than silently breaking callers.
- Keep vendor/protocol details out of the universal core.
- Treat UI enablement, authorization, requested state, applied state, and observed state as separate concepts.
- Keep simulated, sandbox, runtime, hardware-in-loop, and release-candidate claims separate.
- Update docs in the same sprint as code when behavior, boundaries, tests, or package identity changes.
- Prefer changed-area tests during inner-loop development and package/readiness gates at closeout.
- Keep proof artifacts concise, named, and copy/paste friendly.

## Required proof bundle

Each sprint should produce a proof bundle under `proof/` containing at least:

| Artifact | Purpose |
|---|---|
| baseline file snapshot | Establish before-edit state for regression comparison. |
| scope boundary | Declare what was and was not allowed to change. |
| touched-file ledger | Summarize all modified/added/removed files. |
| validation status | Capture commands, results, and known caveats. |
| no-runtime-change or behavior-change declaration | Prevent unclear package claims. |

## Validation selection model

Every sprint must choose validators deliberately:

| Gate type | When required |
|---|---|
| Changed-area unit/contract tests | Required when affected source behavior changes. |
| Focused acceptance tests | Required when a capability boundary is advanced. |
| Governance/readme/document validators | Required when docs, registries, package identity, or entry surfaces change. |
| Package/handoff validators | Required at every package closeout. |
| Hardware-in-loop tests | Required only for sprints claiming real-device behavior. |
| Long-run/performance tests | Required for acquisition, historian, graphing, and stability claims. |
| Advisory diagnostics | Optional unless the sprint explicitly depends on their output. |

## Closeout checklist

A sprint is not closed until:

1. `WORKPLAN_CURRENT_RUN.md` describes the completed run.
2. `NEXT_ACTIONS.md` identifies the next intended run and why.
3. `KNOWN_LIMITATIONS.md` is updated for remaining deferrals.
4. Release notes distinguish behavior changes from governance/doc changes.
5. Relevant active docs and registries are updated.
6. Active/historical lane rules are maintained.
7. Required validators/tests are run and summarized.
8. Generated junk is cleaned before final packaging.
9. Windows path budget is checked against the intended extraction root.
10. The package zip opens into one root folder with `ACTIVE/` and `HISTORICAL/` lanes.

## Active/historical lane rules

- Current working docs live in `ACTIVE/`.
- Superseded current docs move to `HISTORICAL/` only through a documented transition.
- Historical docs are reference/lineage material unless an active doc explicitly promotes or cites them.
- Filename suffixes such as `__WIP` are not authoritative by themselves; the registry and document control header govern classification.
- `NEXT_ACTIONS.md` is the immediate planning surface; the roadmap is the longer sequence surface.
- `WORKPLAN_CURRENT_RUN.md` describes only the current run.

## Sprint sequence maintenance

When a sprint is completed, deferred, split, combined, or reordered, update:

- roadmap document
- sprint sequence JSON and CSV registers
- `NEXT_ACTIONS.md`
- `WORKPLAN_CURRENT_RUN.md`
- release notes
- known limitations/debt records if applicable

The sprint sequence is a control system, not a prediction. Changes are allowed when documented and justified.
