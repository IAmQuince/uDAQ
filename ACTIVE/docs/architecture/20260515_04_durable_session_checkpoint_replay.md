# Durable Session / Checkpoint / Replay Spine — 20260515_04

**Controlled architecture note**  
ID: UDQ-ARCH-NOTE-20260515-04  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture / GPT-5.5 Leader  
Authority: DERIVED

## Package identity
- Package ID: `UDQ-PKG-20260515-04-SESSION-R01`
- Sprint: `20260515_04_session`

## Purpose
The durable session spine captures review-safe sessions and checkpoints around the authoritative runtime-state snapshot model. It is a foundation for future restore, replay, diagnostics, and historian work without implementing production historian behavior.

## Public entry points
- `universaldaq.session.DurableSession`
- `universaldaq.session.SessionCheckpoint`
- `universaldaq.session.ReplayView`
- `universaldaq.session.SessionSafetyPosture`
- `universaldaq.session.DurableSessionService`
- `universaldaq.session.canonical_json(...)`
- `universaldaq.session.state_hash(...)`

## Runtime-state integration
Checkpoints embed the JSON-compatible output of `RuntimeStateSnapshot.to_dict()` or a mapping supplied by a caller. Session services call `build_authoritative_runtime_snapshot()` when no snapshot is supplied, so checkpoints continue to flow through the runtime-state spine rather than bypassing it.

## Replay semantics
Replay is explicitly non-live. A replay view may support review, diagnostics, UI reconstruction, regression tests, training, and later comparison workflows. It must not be interpreted as live hardware state, live command permission, physical output authority, or proof of current observed hardware condition.

The safety flags remain:
- `hardware_mutation_enabled: false`
- `live_mapping_apply_enabled: false`
- `replay_is_live: false`
- `production_historian_enabled: false`

## Validation semantics
Checkpoint validation requires:
- a safety posture;
- false live/mutation flags;
- an embedded runtime snapshot;
- preserved `requested_state`, `applied_state`, and `observed_state` channels.

Unsafe persisted flags are rejected by validation rather than silently normalized.

## Explicitly deferred
- live hardware replay;
- hardware writes;
- live mapping apply;
- production historian storage/indexing;
- runtime logic deployment;
- treating replayed checkpoint data as current observed hardware truth.
