---
document_id: "UDQ-IMP-SPEC-002"
title: "Pre-Code Scaffolding and Verification Structure Specification"
revision: "r0"
status: "WIP"
document_class: "implementation_spec"
owner: "UniversalDAQ"
depends_on:
  - "UDQ-IMP-MAP-001"
  - "UDQ-GOV-SPEC-004"
  - "UDQ-GOV-SPEC-005"
  - "UDQ-REQ-MAT-001"
revision_history:
  - "r0 | 2026-03-21 | Introduced the governed pre-code scaffolding layer for tests/, tools/, tests/data snapshots, and first-slice src package markers."
---
# Pre-Code Scaffolding and Verification Structure Specification [SEC:UDQ-IMP-SPEC-002::0]

## 1. Purpose [SEC:UDQ-IMP-SPEC-002::1]
This specification defines the last package layer that should be created before the first app code sprint: a governed set of tests, tools, snapshots, and package markers that make the first code sprint hard to do wrong.

## 2. Governed tests tree [SEC:UDQ-IMP-SPEC-002::2]
The initial governed `tests/` subtrees are:
- `meta` for declaration/reference hygiene checks
- `smoke` for package-load and package-marker checks
- `contract` for execution-contract-aligned behavior tests
- `scenario` for worked-example-aligned scenario tests
- `invariants` for runtime-conformance hook checks
- `fixtures` for reusable fake objects and builders
- `data` for generated first-slice snapshots and sample traces
- `regression`, `integration`, and `baselines` as reserved governed placeholders

## 3. Governed tools tree [SEC:UDQ-IMP-SPEC-002::3]
The initial governed `tools/` subtrees are:
- `governance` for building derived first-slice snapshots
- `traceability` for reference validation and traceability reporting
- `audit` for reusable scaffold audit helpers
- `diagnostics` for human-readable pre-code diagnostics
- `package_build` for package assembly and cleanup helpers
- `proof` for proof-bundle skeleton helpers
- `dev` for local convenience wrappers that still respect governed outputs

## 4. Snapshot rule [SEC:UDQ-IMP-SPEC-002::4]
The package shall generate current first-slice snapshots under `tests/data/` for:
- requirement pack
- execution contract
- invariant registry
- worked examples
- representative sample scenario traces

## 5. First-slice package-marker rule [SEC:UDQ-IMP-SPEC-002::5]
The package shall include minimal `__init__.py` markers and local guardrail `README.md` files for each first-slice module area so that future code starts from explicit boundaries rather than empty folders.
