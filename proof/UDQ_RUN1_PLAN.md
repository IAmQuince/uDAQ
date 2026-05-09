# UniversalDAQ Run 1 Plan

Package: `20260323_03_runtime_spine`

## What was planned before the five-run broadening discussion

The original next step was a single bounded runtime-quality sprint built on the support-pack boundary that had already been frozen.

That plan had five main goals:

1. Preserve the hardware-agnostic core and keep support packs optional.
2. Treat the real U6 proof as a milestone rather than broadening hardware scope.
3. Deepen one bounded live read-side slice with variable-backed monitoring.
4. Make runtime efficiency structural through scoped recomputation and instrumentation.
5. Improve long-run trustworthiness with bounded buffers, append-only journaling, and explicit stale/degraded/reconnect evidence.

In plain terms, the pre-broadening plan was:

**freeze the optional support-pack model and finish the runtime-quality spine without turning the sprint into a broad architecture or documentation wave.**

## Run 1 of the five-run sequence

Run 1 remains very close to that original plan.

### Purpose

Finish the runtime spine enough that later runs can add events/alarms, command admission, and rules/sequences without inventing side channels or duplicate truth stores.

### Scope

Run 1 focuses on six tightly related code areas:

1. **Runtime lane separation**
   - acquisition capture
   - processing cycle accounting
   - presentation staging/coalescing
   - append-only persistence

2. **Scoped recomputation discipline**
   - keep changed-signal-scoped behavior visible and measurable
   - record impacted and skipped variable work

3. **Bounded hot-path memory**
   - bounded acquisition queue
   - bounded presentation queue
   - bounded recent sample/event/cycle history

4. **Durable runtime truth**
   - append-only JSONL journal
   - queue-backed flushes
   - disconnect/reconnect state events persisted alongside samples/cycles

5. **Runtime observability**
   - poll timing
   - processing timing
   - queue depth, drops, and age
   - journal flush count and write count
   - presentation publish/coalesce counts

6. **One bounded live-monitor slice**
   - discover
   - activate
   - poll
   - bind
   - evaluate variables
   - journal samples and state transitions
   - survive reconnect

### Out of scope

Run 1 intentionally keeps these out:

- no streaming subsystem
- no broad UI redesign
- no deep workbench expansion
- no command arbitration or rules engine work
- no broad hardware-family growth
- no full historian/replay UI

### Why this run comes first

The later runs need a stable runtime spine:

- events/alarms need canonical runtime truth
- command admission needs stable state, evidence, and review bundles
- rules/sequences need both runtime truth and a safe command lane
- the integration run needs all of those sections to share one platform backbone
