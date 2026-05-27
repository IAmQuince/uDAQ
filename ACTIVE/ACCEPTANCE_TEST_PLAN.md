# Acceptance test plan — 20260515_04_session

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`
Active sprint target: `20260515_04_session`

## Required automated tests

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/session/ tests/contract/ -q
```

Expected Sprint 3 coverage:

- session metadata creation and schema versioning,
- checkpoint serialization round trip,
- deterministic checkpoint hash,
- restore into non-authoritative review/session projection,
- corrupt or unsupported checkpoint rejection,
- replay evidence summary generation.

## Required inherited regression tests

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/ -q
```

Inherited tests must continue to prove the Sprint 1 sandbox mapping boundary and Sprint 2 runtime-state projection boundary.

## Required package checks

```bash
PYTHONDONTWRITEBYTECODE=1 python -m tools.audit.run_master_audit --package-root . --profile package-normalization
PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_impact --package-root .
PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_package_entry_surfaces --package-root .
PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_readme_control --package-root .
PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_debt --package-root .
PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.validate_windows_path_budget --package-root . --delivery-root udq_s02b_r01
PYTHONDONTWRITEBYTECODE=1 python -m tools.dev.run_session_checkpoint_smoke --package-root .
PYTHONDONTWRITEBYTECODE=1 python -m tools.diagnostics.dump_session_replay_evidence --package-root . --output audit_reports/testing/session_replay_evidence.json
PYTHONDONTWRITEBYTECODE=1 python -m tools.dev.run_shell_smoke --package-root .
PYTHONDONTWRITEBYTECODE=1 python -m tools.dev.run_labjack_u6_smoke --package-root .
```

## Manual user test

When Sprint 3 UI hooks exist, use the Testing menu to create a session checkpoint, restore it into review/session state, and export replay evidence. Until then, use the no-hardware CLI/dev harness.

## Safety boundary

Passing Sprint 3 acceptance must not imply live mapping apply, hardware output writes, historian production storage, or runtime logic deployment.

- Testing menu exposes `Export Session Replay Evidence` as a review-only no-hardware proof path.
