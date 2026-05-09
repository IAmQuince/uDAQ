# Next Sprint Candidate Register - 2026-03-26

## Ranked candidates promoted from assessment and maintainer guidance

### Priority 1 - log hardening
- move the journal from ephemeral temp storage to a governed runtime path
- add monotonic `sequence_id` to journal entries
- add `fsync` after flush on the durability boundary
- segment long-running journals and emit a lightweight manifest

### Priority 2 - checkpoint and recovery
- introduce a durable `SessionCheckpoint` snapshot
- recover from checkpoint plus journal tail rather than replaying entire session history
- preserve alarm state, variable snapshots, device lifecycle phase, and profile/workspace posture

### Priority 3 - tiered history
- keep hot history in bounded queues
- add warm summary buckets per signal
- index cold journal segments by time range and signal presence

### Priority 4 - replay and state-hash
- formalize journal event vocabulary
- add replay harness for deterministic reconstruction
- attach state hash to checkpoints so replay divergence becomes mechanically detectable

## Deferred-but-captured reviewer suggestions
- split `RuntimeQualityService` only when the compatibility boundary is protected
- simplify duplicated CSV/JSON registry production after current package truth remains stable
- keep `NullMetrics` / lazy-metrics / running-counter work bounded to measured payoffs
