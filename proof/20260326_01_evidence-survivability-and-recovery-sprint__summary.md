# 20260326_01 Evidence Survivability and Recovery Sprint — Proof Summary

## Proof statement
This bounded sprint strengthens the runtime evidence substrate by adding durable session journaling, manifest-backed segment enumeration, checkpoint persistence, and bounded replay of the journal tail after the last committed checkpoint.

## Code surfaces touched
- `src/universaldaq/runtime/models.py`
- `src/universaldaq/runtime/services.py`
- `src/universaldaq/runtime/__init__.py`
- `src/universaldaq/app/bootstrap.py`
- `src/universaldaq/app/automation_review_handler.py`

## Proof tests added
- `tests/contract/test_contract_runtime_journal_survivability_and_recovery.py`
- `tests/integration/test_integration_runtime_checkpoint_bundle_surface.py`

## Acceptance evidence for this bounded sprint
- ordered `sequence_id` persists across rotated session journal segments
- journal manifest enumerates the bounded segment chain
- checkpoint payloads carry a state hash and can be loaded through the latest-valid path
- lifecycle review bundle exposes checkpoint summary and bounded recovery-bundle metadata
- compatibility callers that request a single journal file still receive that file
