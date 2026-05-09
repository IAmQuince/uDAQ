# Tools

This tree holds package-support tooling only. It covers governance, audit, traceability, diagnostics, packaging, proof, and developer workflow helpers. The preferred audit entrypoint is `python -m tools.audit.run_master_audit`, the preferred sprint documentation-control validator is `python -m tools.governance.validate_document_impact`, and the preferred README-control validator is `python -m tools.governance.validate_readme_control`.

- `tools/governance/validate_document_debt.py` — validates the documentation-update debt register workflow.
