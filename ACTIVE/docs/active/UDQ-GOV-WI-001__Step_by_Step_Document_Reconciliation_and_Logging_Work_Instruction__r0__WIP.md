---
document_id: UDQ-GOV-WI-001
title: Step-by-Step Document Reconciliation and Logging Work Instruction
revision: r0
status: WIP
document_class: governance_work_instruction
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-SOP-001"
  - "UDQ-GOV-TPL-001"
  - "UDQ-GOV-TPL-002"
  - "UDQ-GOV-REG-003"
  - "UDQ-GOV-POL-002"
revision_history:
  - "r0 | 2026-03-22 | Introduced the required step-by-step procedure for reviewing documents, deciding whether they must change, logging outcomes, and closing a bounded package without silent documentation drift."
---
# Step-by-Step Document Reconciliation and Logging Work Instruction [SEC:UDQ-GOV-WI-001::0]

## 1. Purpose [SEC:UDQ-GOV-WI-001::1]

This work instruction defines the exact steps that shall be followed during a bounded change to make sure all affected documentation is reviewed, updated when needed, and logged correctly when update is deferred.

## 2. Trigger [SEC:UDQ-GOV-WI-001::2]

Follow this procedure for every bounded sprint, package revision, hotfix, document-only revision, or code change that could affect meaning, scope, status, package composition, tests, tooling, or release-facing summaries.

## 3. Required working artifacts [SEC:UDQ-GOV-WI-001::3]

Before making changes, open or prepare all of the following:
- the governing source docs and ADRs for the change
- `UDQ-GOV-TPL-001` for the documentation impact map
- `UDQ-GOV-TPL-002` for the running documentation review ledger
- `UDQ-GOV-REG-003` for any intentionally deferred stale assets
- the current release notes, manifest, and executive summary
- the current document and README registries

## 4. Required outcomes per reviewed asset [SEC:UDQ-GOV-WI-001::4]

Every reviewed controlled asset shall end the bounded change with exactly one outcome:
- `UPDATED` — the asset changed in this bounded change
- `REVIEWED_OK` — the asset was reviewed and is still correct
- `DEFERRED_STALE` — the asset is stale and not updated now; it must be logged in `UDQ-GOV-REG-003`
- `SUPERSEDED` — the asset is replaced by a newer controlled asset in the same bounded change
- `GENERATED_NOCHANGE` — the asset was regenerated and remains materially unchanged
- `OUT_OF_SCOPE` — the asset was considered but proven unrelated to the bounded change

No reviewed asset may remain without an outcome.

## 5. Step-by-step procedure [SEC:UDQ-GOV-WI-001::5]

### Step 1 — Define the bounded change
Record:
- change summary
- governing source docs / ADRs
- modules expected to change
- user-visible effects if any
- proof outputs expected at closeout

### Step 2 — Open the documentation impact map
Fill in `UDQ-GOV-TPL-001` with all currently known:
- affected modules
- affected requirement IDs
- affected invariant IDs
- affected tests / proof outputs
- affected controlled docs
- affected controlled entry documents / READMEs
- affected registries / generated snapshots
- reviewed but intentionally unchanged docs / READMEs
- reviewed but intentionally deferred docs

### Step 3 — Open the running documentation review ledger
Create a working copy of `UDQ-GOV-TPL-002` or reproduce its table in the PR / review package.

For every controlled asset reviewed during the change, add a ledger row before closeout.

### Step 4 — Build the review candidate set
Review candidates shall include, at minimum, any asset in these categories that could be affected:
- active controlled specs, standards, SOPs, narratives, plans, and reports
- ADRs
- controlled READMEs and handbook / release / review docs
- machine-readable registries and snapshots
- package markers and module READMEs
- release notes, manifest, executive summary, and save-point summary
- validators, audits, and meta tests that enforce documentation policy

### Step 5 — Classify each candidate
For each candidate asset, decide one of the following:
- must update now because semantics, scope, status, or package truth changed
- review only because it remains correct
- defer because it is stale but outside the bounded change
- supersede because a new revision or replacement asset is being created
- mark out of scope because it is not actually affected

Record that decision in the ledger immediately.

### Step 6 — Update governing sources first
If the change affects meaning, boundaries, definitions, package identity, or operational procedure, update in this order:
1. governing spec, glossary, SOP, or ADR
2. contradiction / duplication / debt registers and the running ledger
3. requirement / invariant / coverage / consistency registries if affected
4. snapshots, fixtures, and proof expectations
5. code and package markers
6. tests and diagnostics
7. controlled READMEs and handbook / release / review docs
8. release notes, manifest, executive summary, and save-point summary

### Step 7 — Apply the no-silent-carryover rule
If a reviewed asset is stale and you are not updating it now:
- set the ledger outcome to `DEFERRED_STALE`
- create or update a debt entry in `UDQ-GOV-REG-003`
- include the owner, target, disposition, and status
- reference the debt ID back in the ledger row

A stale reviewed asset may not be left behind silently.

### Step 8 — Reconcile generated and registry artifacts
When docs or controlled READMEs change, review whether any of the following must also change:
- document registry
- README registry
- requirement registry
- invariant registry
- execution contract
- implementation coverage matrix
- consistency findings
- release manifest
- proof outputs or audit outputs

If an affected generated asset is not updated now, log it in the ledger and, if stale, in `UDQ-GOV-REG-003`.

### Step 9 — Reconcile handbook and release surfaces
After the governing layer and code/tests are updated, reconcile the human entry surfaces:
- root README
- handbook docs
- release docs
- review docs

These documents shall not claim an older repo state once the bounded change closes.

### Step 10 — Close the ledger before running the gate
Before validation, verify that every reviewed asset has:
- an outcome
- an owner if needed
- a source / rationale
- a debt reference if deferred stale
- a note if intentionally unchanged

### Step 11 — Run validation
Run, at minimum:
- `python -m tools.governance.validate_document_impact --package-root .`
- `python -m tools.governance.validate_readme_control --package-root .`
- `python -m tools.governance.validate_document_debt --package-root .`
- `python -m tools.audit.run_master_audit --package-root . --profile document-procedure`
- `python -m tools.dev.run_local_gate --package-root .`

### Step 12 — Package closeout
Update and confirm:
- release notes
- release manifest
- executive summary
- next actions
- save-point summary if relevant
- document registry / README registry if affected
- debt register and contradiction / duplication registers if affected

Then archive superseded controlled revisions and build the review package.

## 6. Decision rules for whether a document must change [SEC:UDQ-GOV-WI-001::6]

A document shall be updated in the same bounded change when any of the following is true:
- it states a repo, package, or subsystem status that is no longer true
- it names a revision, file path, package ID, validator, or procedure that changed
- it describes a boundary, responsibility, or behavior that changed
- it governs a reviewer or contributor action that changed
- it is a release-facing summary whose narrative changed materially

A document may remain unchanged when it was reviewed and one of the following is true:
- it is still accurate
- it is derived and still accurately reflects its sources
- it is unrelated to the bounded change

## 7. Required logging rules [SEC:UDQ-GOV-WI-001::7]

- The impact map captures the planned review surface.
- The running review ledger captures the outcome for every reviewed asset.
- The debt register captures every stale reviewed asset that is intentionally deferred.
- The release notes capture what changed in the package.

The impact map is not a substitute for the ledger.
The ledger is not a substitute for the debt register.

## 8. Closeout acceptance criteria [SEC:UDQ-GOV-WI-001::8]

Do not close the bounded change until all of the following are true:
- every reviewed controlled asset has an outcome in the ledger
- every deferred stale asset has a debt entry
- all changed controlled READMEs have updated control strips and registry entries
- all affected release-facing documents are reconciled
- superseded active revisions are archived
- validators and tests pass
- the package can be reviewed without relying on oral history
