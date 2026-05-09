## Summary
- What changed:
- Governing source(s):

## Documentation impact map
- Affected modules:
- Affected requirement IDs:
- Affected invariant IDs:
- Affected tests / proof outputs:
- Affected controlled docs:
- Affected controlled READMEs:
- Affected registries / snapshots:
- Reviewed but intentionally unchanged docs:
- Reviewed but intentionally unchanged READMEs:
- Reviewed but intentionally deferred docs logged in `UDQ-GOV-REG-003`:

## Documentation review ledger summary
- Location of the running ledger (`UDQ-GOV-TPL-002` or equivalent):
- Assets reviewed:
- Assets marked `UPDATED`:
- Assets marked `REVIEWED_OK`:
- Assets marked `DEFERRED_STALE`:
- Assets marked `SUPERSEDED`:

## Checklist
- [ ] Followed `UDQ-GOV-WI-001` step by step
- [ ] Governing spec / ADR updated if needed
- [ ] Requirement / invariant / coverage artifacts updated if needed
- [ ] Running documentation review ledger completed with outcomes for all reviewed assets
- [ ] Debt register updated for any intentionally deferred stale docs
- [ ] Tests and snapshots updated
- [ ] Controlled READMEs updated or explicitly reviewed
- [ ] Executive summary, implementation entry, next actions, and release notes updated
- [ ] `python -m tools.governance.validate_document_impact --package-root .`
- [ ] `python -m tools.governance.validate_readme_control --package-root .`
- [ ] `python -m tools.governance.validate_document_debt --package-root .`
- [ ] `python -m tools.dev.run_local_gate --package-root .`
