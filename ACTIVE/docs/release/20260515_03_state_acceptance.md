# Acceptance note — 20260515_03_state

**Controlled release companion document**  
ID: UDQ-REL-STATE-ACCEPT-20260515-03  
Status: CLOSED
Revision: r0  
Owner: Core Architecture / GPT-5.5 Integration
Authority: DERIVED  
Source docs: UDQ-HANDBOOK-NEXT-001, UDQ-ROADMAP-SPEC-001, UDQ-SPRINT-REG-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Closeout status

The integrated `20260515_03_state` package is closed for merge/release handoff on branch `cursor/20260515_03_state-integration`. It merges the leader runtime-state spine, contract/governance helper coverage, and runtime-state diagnostic tooling without starting the next feature sprint.

## Sprint objective

Define the acceptance contract for the authoritative runtime state model so one inspectable truth surface can represent devices, points, mappings, signals, variables, command posture, safety posture, logic posture, degraded conditions, and review projections without granting live hardware authority.

## Non-goals

- No live mapping apply.
- No hardware writes.
- No physical output authority.
- No production historian behavior.
- No runtime logic deployment.
- No vendor-specific leakage into the universal core.
- No broad controller refactor in this helper branch.

## Runtime-state acceptance criteria

- The authoritative runtime snapshot exposes a stable `model_version`.
- The snapshot exposes `snapshot_id` and `captured_at` identity fields.
- Empty/no-device runtime state is valid and serializable.
- Requested, applied, and observed states remain separate rather than flattened into one vague status.
- Simulated, unavailable, recovering, stale, and unknown/degraded conditions are explicit in the snapshot.
- Command posture, safety posture, and logic posture are represented without authorizing hardware writes.
- Serialization is deterministic enough for diagnostics and review tooling.

## Sandbox boundary acceptance criteria

- Sandbox mapping drafts/proposals remain explicitly non-authoritative.
- Sandbox mapping state is not treated as authoritative applied runtime state.
- Sandbox rollback does not mutate authoritative applied state.
- Any runtime-state diagnostic or review projection must keep sandbox-only posture visible as draft/review/prepared-request/diagnostic rather than live applied.

## Degraded-condition acceptance criteria

- No devices discovered is a valid state.
- Simulated devices are explicit rather than implied.
- Device disappearance is explicit.
- Device reappearance can be represented as recovering/stale instead of silently healthy.
- Stale signals remain serializable and reviewable.
- Optional hardware support-pack absence does not break `universaldaq.runtime` imports.

## Governance acceptance criteria

- Mapping sandbox boundary tests retain `TEST_DECLARATION` metadata.
- Package entry registry exposes a canonical `review_entry`.
- Package-root allowlist matches the active package front-door layout.
- Retained pass2 traceability documents exist under `docs/release/history/`.
- Documentation-impact phrase guards are satisfied by current entry docs.

## Accepted debt / non-blocking note

| debt_id | asset | class | finding | disposition | owner | target | status |
|---|---|---|---|---|---|---|---|
| UDQ-STATE-ACCEPT-DEBT-001 | `src/universaldaq/app/controller.py`; `tests/meta/test_meta_controller_decomposition.py` | governance_test | Controller concentration remains above the current decomposition threshold and is not safe to refactor broadly in this helper branch. | Accepted for this sprint helper branch because the runtime-state contract/tests and governance scaffolding can merge independently without changing controller behavior. | Core Architecture / GPT-5.5 leader | Future controller decomposition pass after runtime-state merge stabilizes the architectural seam. | OPEN |

## Validation commands

- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/meta -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/contract -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/invariants -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/unit/test_mapping_sandbox_state.py -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/unit/test_mapping_sandbox_diff.py -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/unit/test_runtime_state_serialization.py -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/contract/test_mapping_apply_sandbox_boundary.py -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/contract/test_mapping_apply_rollback.py -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/contract/test_authoritative_runtime_state_contract.py -q`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/invariants/test_runtime_state_boundaries.py -q`
- `python3 -m ruff check <touched files>`

## What GPT-5.5 must demonstrate

- Export the authoritative runtime-state API through `universaldaq.runtime` with `RuntimeStateSnapshot` and/or `build_runtime_state_snapshot`.
- Satisfy the contract tests without flattening requested/applied/observed state.
- Keep sandbox-only mapping posture non-authoritative.
- Keep command and safety posture representational only, not live-write-authoritative.

## What Codex 5.3 diagnostic tooling should demonstrate

- Diagnostic commands can serialize and print the authoritative runtime snapshot deterministically.
- Snapshot output clearly preserves simulated/unavailable/recovering/stale states.
- Diagnostics do not require optional hardware libraries for core runtime imports.
- Snapshot/report tooling does not mislabel sandbox drafts as live applied state.

## Merge-order recommendation

1. Merge GPT-5.5 runtime-state branch first.
2. Merge this GPT-5.4 contract/tests/governance branch second and adapt the runtime-state API export if needed.
3. Merge Codex 5.3 diagnostics branch third so it can bind to the merged runtime-state API.
