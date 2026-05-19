# UniversalDAQ — Save-Point Review Ledger

This ledger records the main assets reviewed during the historian/export sprint built on the shell-semantics baseline and the original save-point baseline.

| asset_path | asset_id | class | review_scope | outcome | action_taken | debt_id | owner | notes |
|---|---|---|---|---|---|---|---|---|
| README.md | UDQ-README-ROOT-001 | controlled_readme | package disposition | UPDATED | reframed from shell-semantics baseline to historian/export baseline |  | Core Architecture | entry summary now describes manifest-backed exports |
| docs/release/EXEC_SUMMARY.md | UDQ-README-EXEC-001 | controlled_readme | package summary | UPDATED | updated to describe completed historian/export depth sprint |  | Core Architecture | aligns summary with actual code scope |
| docs/release/RELEASE_NOTES.md | UDQ-README-RELNOTE-001 | controlled_readme | package notes | UPDATED | changed package id and major changes list |  | Core Architecture | export manifest additions captured |
| docs/release/SAVEPOINT_SUMMARY.md | UDQ-README-SAVEPOINT-001 | controlled_readme | baseline lineage | UPDATED | extended lineage summary to include historian/export depth |  | Core Architecture | keeps save-point lineage visible |
| docs/handbook/IMPLEMENTATION_ENTRY.md | UDQ-README-IMPL-001 | controlled_readme | implementation boundary | UPDATED | changed from shell-semantics baseline to historian/export baseline |  | Core Architecture | non-mutating export posture called out |
| docs/handbook/NEXT_ACTIONS.md | UDQ-README-NEXT-001 | controlled_readme | next-sprint planning | UPDATED | shifted next direction to authorization/authority enforcement depth |  | Core Architecture | reconciliation obligation retained |
| docs/active/UDQ-EXP-SPEC-001__Export_Review_and_Evidence_Bundle_Specification__r0__WIP.md | UDQ-EXP-SPEC-001 | active_doc | export doctrine | UPDATED | added bounded implemented slice and explicit manifest doctrine notes |  | Core Architecture | now matches code surface |
| docs/active/UDQ-HIS-SPEC-001__Historian_Events_and_Evidence_Specification__r3__WIP.md | UDQ-HIS-SPEC-001 | active_doc | evidence relationships | UPDATED | added manifest-backed export and serialization notes |  | Core Architecture | bundle semantics clarified |
| docs/active/UDQ-GAP-RPT-001__Open_Implementation_Gaps__r9__WIP.md | UDQ-GAP-RPT-001 | active_doc | active gaps | UPDATED | moved historian/export from shallow gap to closed bounded slice |  | Core Architecture | authority depth remains next |
| docs/active/UDQ-IMP-PLAN-001__Implementation_Transition_and_Handoff_Plan__r7__WIP.md | UDQ-IMP-PLAN-001 | active_doc | sprint sequencing | UPDATED | recorded historian/export sprint closeout and next authorization sprint |  | Core Architecture | bounded order preserved |
| docs/active/UDQ-REQ-MAT-001__Requirements_Traceability_Matrix__r8__WIP.md | UDQ-REQ-MAT-001 | active_doc | traceability note | UPDATED | noted export/provenance evidence path now exists in code and tests |  | Core Architecture | matrix remains registry-backed |
| docs/active/UDQ-QUAL-DEF-001__Definition_of_Complete_by_Subsystem__r2__WIP.md | UDQ-QUAL-DEF-001 | active_doc | completion criteria | UPDATED | tightened historian/export completion language to include manifests and deterministic payloads |  | Core Architecture | bounded completion clearer |
| src/universaldaq/historian/services.py | n/a | code_asset | export assembly depth | UPDATED | added export intent resolution, manifest build, serialization, and review artifact generation |  | Core Architecture | core sprint implementation |
| src/universaldaq/app/controller.py | n/a | code_asset | shell export orchestration | UPDATED | added export intent and export artifact shell actions |  | Core Architecture | session/result state preserved |
| tools/diagnostics/dump_export_inventory.py | tool | diagnostic_tool | export diagnostics | UPDATED | added manifest-aware export inventory dump |  | Core Architecture | copy-pasteable diagnostic output |
| proof tooling for Ruff and mypy execution evidence | n/a | proof_gap | proof closeout | DEFERRED_STALE | environment still lacks optional dev tools | UDQ-DOCDEBT-012 | Core Architecture | documented in discrepancy inventory |
