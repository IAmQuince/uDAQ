---
document_id: UDQ-GOV-REG-003
title: Documentation Update Debt Register
revision: r4
status: WIP
document_class: governance_register
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-GOV-LOG-001"
  - "UDQ-GOV-SOP-001"
supersedes:
  - "UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r2__WIP.md"
revision_history:
  - "r3 | 2026-03-24 | Restored the full debt register body after accidental truncation during cleanup and preserved the current bounded closeout debt items."
---
# Documentation Update Debt Register [SEC:UDQ-GOV-REG-003::0]

## 1. Purpose [SEC:UDQ-GOV-REG-003::1]

This register records documentation and registry assets that were reviewed, found stale, and either:
- corrected in the current sprint,
- intentionally deferred with an owner and target sprint,
- or kept under observation because the cost of immediate update exceeded the bounded sprint scope.

The point is to stop stale language from surviving only as tribal knowledge.

## 2. Required use [SEC:UDQ-GOV-REG-003::2]

If a contributor notices a materially stale controlled document, controlled entry document, registry, snapshot, or package marker and does **not** update it in the same bounded change, the contributor shall add an entry here before the sprint/package closes.

## 3. Current entries [SEC:UDQ-GOV-REG-003::3]

| debt_id | asset | class | finding | disposition | owner | target | status |
|---|---|---|---|---|---|---|---|
| UDQ-DOCDEBT-001 | docs/active/UDQ-GAP-RPT-001__Open_Implementation_Gaps__r7__WIP.md | active_doc | Gap report still stated typed model work had not started and that 15 behavior tests were placeholders. | Corrected in r8 during the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-002 | docs/active/UDQ-IMP-PLAN-001__Implementation_Transition_and_Handoff_Plan__r5__WIP.md | active_doc | Plan still described the next step as the typed-domain-model sprint rather than the post-shell save-point baseline. | Corrected in r6 during the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-003 | tests/README.md | controlled_readme | Test tree README still said contract, scenario, and invariant behavior tests remained scaffolded. | Corrected in the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-004 | src/universaldaq/__init__.py | package_marker | Package marker still identified the repo as only the Sprint 1 typed-domain-model baseline. | Corrected in the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-005 | src/universaldaq/*/README.md reserved package guardrails | controlled_readme | Several reserved-package READMEs still referenced the "next typed-domain-model sprint" instead of a general later-slice boundary. | Corrected in the save-point reconciliation pass. | Core Architecture | Sprint 1C | CLOSED |
| UDQ-DOCDEBT-006 | tests/data/first_slice_requirement_pack.json; tests/data/first_slice_invariant_registry.json; tests/data/first_slice_execution_contract.json | snapshot | First-slice snapshots still carried the old sprint1-typed-model package ID and scaffold-era status language. | Closed in the save-point freeze package after coherent snapshot regeneration and status-field reconciliation. | Core Architecture | Save-point freeze package | CLOSED |
| UDQ-DOCDEBT-007 | registries/active/universalDAQ_requirement_registry_r9.* | registry | Requirement registry still used scaffold-era language for entries whose bounded first-slice assertions now execute. | Closed in the save-point freeze package after coherent registry regeneration. | Core Architecture | Save-point freeze package | CLOSED |
| UDQ-DOCDEBT-008 | registries/active/universalDAQ_execution_contract_r2.* | registry | Execution-contract registry still carried scaffold-era status language in several fields. | Closed in the save-point freeze package after coherent registry regeneration. | Core Architecture | Save-point freeze package | CLOSED |
| UDQ-DOCDEBT-009 | registries/active/universalDAQ_consistency_findings_r9.json | registry | Consistency findings file still carried an older package identity and needed regeneration. | Closed in the save-point freeze package after package-identity and consistency-report refresh. | Core Architecture | Save-point freeze package | CLOSED |
| UDQ-DOCDEBT-010 | registries/active/universalDAQ_document_registry_r20.* | registry | Document registry had pointed to superseded active revision paths and omitted newer governance procedure assets. | Closed in the document-procedure package after coherent registry regeneration. | Core Architecture | Document procedure package | CLOSED |
| UDQ-DOCDEBT-011 | registries/active/universalDAQ_readme_registry_r0.* | registry | README registry needed refresh so controlled README revisions and source links matched the package truth. | Closed in the document-procedure package after coherent registry regeneration. | Core Architecture | Document procedure package | CLOSED |
| UDQ-DOCDEBT-012 | proof bundle optional dev-tool execution evidence | proof_gap | Ruff and mypy execution evidence remain environment-dependent and may be skipped when those tools are not installed locally. | Leave open until a package is produced in an environment with the optional dev tools installed. | Core Architecture | Next proof-hardening pass | OPEN |
| UDQ-DOCDEBT-013 | package-facing README/release docs after save-point freeze | controlled_readme | Several entry documents still described the save-point freeze package rather than the next shell-semantics sprint built on it. | Closed in the shell-semantics sprint after handbook, release, and review docs were revised coherently. | Core Architecture | Shell-semantics sprint | CLOSED |
| UDQ-DOCDEBT-014 | active UI/profile/historian specs lacking bounded implementation notes | active_doc | Key active specs described intended shell behavior but did not acknowledge the newly implemented bounded controller/session semantics. | Closed in the shell-semantics sprint after bounded implementation notes were added to the touched specs. | Core Architecture | Shell-semantics sprint | CLOSED |
| UDQ-DOCDEBT-015 | docs/handbook/START_HERE.md; docs/handbook/TESTS_AND_TOOLS.md; docs/release/EXEC_SUMMARY.md; docs/release/SAVEPOINT_SUMMARY.md; docs/release/RELEASE_MANIFEST.yaml | controlled_readme | Front-door package docs still described earlier bounded sprint states rather than the lifecycle/binding foundation package. | Closed in the cleanup pass after handbook/release docs were revised coherently to the then-current package truth. | Core Architecture | Lifecycle/binding cleanup pass | CLOSED |
| UDQ-DOCDEBT-016 | docs/active/UDQ-GAP-RPT-001; docs/active/UDQ-IMP-PLAN-001; docs/active/UDQ-GOV-LOG-001; docs/active/UDQ-REQ-MAT-001; docs/active/UDQ-QUAL-DEF-001; docs/active/UDQ-GOV-RPT-001; docs/active/UDQ-GOV-RPT-002 | active_doc | Active governance/current-state docs were lagging the lifecycle/binding/variable/reconciliation package truth. | Closed in the cleanup pass after those active docs were realigned to the then-current bounded package line. | Core Architecture | Lifecycle/binding cleanup pass | CLOSED |
| UDQ-DOCDEBT-017 | registries/active/universalDAQ_readme_registry_r0.*; registries/active/universalDAQ_execution_contract_r2.*; registries/active/universalDAQ_consistency_findings_r9.*; tests/data/first_slice_*.json | registry | Active machine-readable assets still carried older shell-semantics package identity. | Closed in the cleanup pass after package IDs and matching CSV/JSON artifacts were refreshed to the then-current package identity. | Core Architecture | Lifecycle/binding cleanup pass | CLOSED |
| UDQ-DOCDEBT-018 | handbook/release entry-surface identity | controlled_readme | Start-here and review-entry documents relied too heavily on dates and left older entry documents visually ambiguous. | Closed in the package-normalization sprint after formal package IDs, canonical-vs-historical entry marking, and the package-entry registry were added. | Core Architecture | Package-normalization sprint | CLOSED |
| UDQ-DOCDEBT-019 | docs/active/UDQ-GOV-REG-001; docs/active/UDQ-GOV-REG-003 | governance_register | Restored register bodies were no longer truncated but still contained malformed markdown table rows. | Closed in the package-normalization sprint after direct structural repair and validator hardening. | Core Architecture | Package-normalization sprint | CLOSED |
| UDQ-DOC-DEBT-001 | deeper subsystem specs | active_doc | Several subsystem specs still need fuller prose updates to match the bounded proof line, but the closeout only updated the minimum controlled set. | Leave open until the next bounded documentation tightening pass. | Core Architecture | Next documentation tightening pass | OPEN |
| UDQ-DOC-DEBT-002 | handbook/release historical sprawl | controlled_readme | Older historical release/start-here documents still exist for earlier package states and may need archival/retirement work later. | Leave open until the next release-facing documentation cleanup pass. | Core Architecture | Next release-facing cleanup pass | OPEN |
| UDQ-DOC-DEBT-003 | broader architecture records | governance_register | Action-claim and correlation doctrine is now implemented but may later deserve a dedicated ADR if it becomes a long-lived architectural pattern. | Leave open and revisit when the bounded proof line expands. | Core Architecture | Future ADR / architecture pass | OPEN |
| UDQ-DOC-DEBT-004 | legacy filename/front-matter status carryover | governance_register | Many controlled documents still carry older `__WIP` filename markers or `status: WIP` front matter even though current review surfaces now use a stricter two-axis classification model. | Leave open until a dedicated governance cleanup pass renames legacy files, aligns lifecycle metadata, and regenerates registries under the stricter classification rules. | Core Architecture | Future classification migration pass | OPEN |
| UDQ-DOCDEBT-020 | package-facing review/docs after gap run | controlled_readme | README, handbook, release, and proof-index surfaces still needed one final synchronization pass so the successful U6 proof, LabJack/core-boundary verification, and next-sprint plan all appeared coherently for external review. | Closed in the documentation-alignment run after package-facing docs, manifest/registry surfaces, and requirement/spec status narratives were synchronized. | Core Architecture | Documentation alignment run | CLOSED |
| UDQ-DOCDEBT-021 | active UI / signal / graph / logic docs after 20260330_05 | active_doc | Controlled docs lagged the device-centered Device I/O Inspector, canonical tag model, semantic top bar, honest trace feature status, and first draft/simulated Logic slice. | Closed in the 20260330_06 documentation reconciliation package after release surfaces and active specs were synchronized. | Core Architecture | 20260330_06 documentation closeout | CLOSED |
| UDQ-DOCDEBT-022 | live secondary-axis trace behavior | active_doc | The package documents secondary-axis assignment but the current runtime still does not provide a true live multi-axis implementation. | Leave open until a bounded graph-depth sprint provides live secondary-axis behavior and proof. | Core Architecture | Future graph-depth sprint | OPEN |
| UDQ-DOCDEBT-023 | authoritative binding availability across all runtime contexts | governance_register | Current package documentation distinguishes `Applied`, `Draft`, `Unavailable`, and `Unmapped`, but authoritative binding readback is still unavailable in some bounded runtime contexts. | Leave open until later controller-backed readback closure. | Core Architecture | Future authoritative-readback sprint | OPEN |
| UDQ-DOCDEBT-024 | controller-backed mapping apply and runtime-authoritative logic deployment | governance_register | Device-centered configuration and draft/simulated Logic Designer behavior are now documented, but shell-side apply through the controller seam and runtime-authoritative logic deployment remain deferred. | Leave open until later implementation sprints close those authority paths. | Core Architecture | Future apply/logic-authority sprint | OPEN |

## 4. Closure rule [SEC:UDQ-GOV-REG-003::4]

A debt entry closes only when the affected asset is updated or explicitly superseded and the closeout is reflected here with the disposition changed to CLOSED.

