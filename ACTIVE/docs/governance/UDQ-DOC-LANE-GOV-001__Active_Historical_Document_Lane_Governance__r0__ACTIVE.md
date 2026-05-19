# Active / historical document lane governance

**Controlled document**  
ID: UDQ-DOC-LANE-GOV-001  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture  
Authority: PRIMARY  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Purpose

Define how UniversalDAQ handoff packages separate current working material from historical/reference material.

## Lane definitions

### ACTIVE

`ACTIVE/` contains the current authoritative package baseline. Future implementation, documentation, testing, and validation work starts here unless a task explicitly requires historical comparison.

### HISTORICAL

`HISTORICAL/` contains superseded packages, old release/audit evidence, original uploaded archives, external references, and reconciliation ledgers. Historical documents are not authoritative unless promoted by a governed transition.

## Document states

| State | Meaning |
|---|---|
| ACTIVE | Current authoritative document |
| WIP | Current but incomplete; maintained in active lane |
| REVIEW | Candidate active document under review |
| SUPERSEDED | Replaced by a newer active document |
| HISTORICAL | Retained only for traceability |
| REFERENCE | Non-authoritative reference material |
| EXTERNAL | Imported outside reference/reviewer material |
| QUARANTINED | Retained but known to be stale, confusing, or unsafe as current truth |

## When to update ACTIVE

Update `ACTIVE/` when a change affects current behavior, requirements, specifications, source, tests, validation evidence, package entry points, release notes, known limitations, next actions, or active registries.

## When to update HISTORICAL

Update `HISTORICAL/` when active material is superseded, a prior package is imported, an external review is added, stale material is reconciled, old audit evidence is retired, or lineage context must be preserved.

## When to update both

Update both lanes when a document is promoted, retired, superseded, or reconciled. Every lane transition must update:

- `registries/document_transition_registry.yaml`
- `registries/active_document_registry.yaml`
- `registries/historical_document_registry.yaml`
- `PACKAGE_MANIFEST.md`
- relevant release/handbook entries

## Promotion rule

Historical material may become active only after review, current-package identity update, state update, registry update, and supersession of any replaced active document.

## Retirement rule

Active material moved to history must no longer carry a misleading `ACTIVE` filename/state unless quarantined and documented.
