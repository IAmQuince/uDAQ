# Explorer Interface Prep — 20260515_05

**Controlled architecture note**  
ID: UDQ-ARCH-NOTE-20260515-05-PREP  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture / GPT-5.5 Integration  
Authority: DERIVED

## Purpose

This note prepares the next `20260515_05_explorer` sprint without implementing the full Explorer UI. The Explorer should consume existing runtime, session, and mapping APIs rather than creating a parallel state model.

## Existing inputs

- Runtime truth spine: `universaldaq.runtime.RuntimeStateSnapshot` and `build_authoritative_runtime_snapshot(...)`.
- Session/replay spine: `universaldaq.session.DurableSession`, `SessionCheckpoint`, `ReplayView`, and `DurableSessionService`.
- Sandbox mapping proof: `universaldaq.mapping.MappingSandboxState` and sandbox apply/rollback results.
- Diagnostics: `tools.diagnostics.dump_runtime_state_snapshot` and `tools.diagnostics.dump_session_checkpoint`.

## Explorer boundaries

- Device Explorer should present discovered devices, adapters, raw points, lifecycle state, and degraded/unavailable posture.
- Signal Explorer should present canonical signals, variables, derived values, freshness, stale/degraded/unavailable posture, and requested/applied/observed truth channels.
- Mapping Explorer should distinguish sandbox draft/proposal/preflight/review/prepared-request state from authoritative applied/review state.
- Session/Replay Explorer should present checkpoint summaries, replay-safe runtime state, and non-live replay posture.

## Non-goals for this integration branch

- No full Device Explorer / Signal Explorer UI.
- No live hardware writes.
- No live mapping apply.
- No production historian.
- No replay-as-live behavior.
- No collapse of requested, applied, and observed runtime semantics.

## Integration guidance

The Explorer sprint should build projection/view-model adapters over these APIs. It should not mutate `RuntimeStateSnapshot`, promote sandbox mappings to applied state, or treat `ReplayView` data as current observed hardware truth.
