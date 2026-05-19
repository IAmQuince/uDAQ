# Handoff package governance

**Controlled document**  
ID: UDQ-PKG-HANDOFF-GOV-001  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture  
Authority: PRIMARY  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Required package structure

A handoff package must unzip as exactly one root folder containing:

- `ACTIVE/`
- `HISTORICAL/`
- `ROOT_PACKAGE_INDEX.md`

## Naming rule

The zip basename and root folder name must match exactly. For this package:

- Zip: `20260515_02_mapping.zip`
- Root folder: `20260515_02_mapping/`

## Current package identity rule

The current package ID must be consistent across:

- `ROOT_PACKAGE_INDEX.md`
- `ACTIVE/README_START_HERE.md`
- `ACTIVE/README.md`
- `ACTIVE/PACKAGE_MANIFEST.md`
- `ACTIVE/config/package_metadata.json`
- `ACTIVE/docs/release/RELEASE_MANIFEST.yaml`
- `ACTIVE/docs/release/PACKAGE_ENTRY_REGISTRY.yaml`
- active review-start document

## Path-budget rule

The package should remain safe to extract under `C:\Users\iaq16\Documents\Code\uDAQ`. Long paths must be flagged in active audit reports.

## Historical inclusion rule

Prior packages may be included as original archives and/or documentation snapshots. Their presence does not make them current.
