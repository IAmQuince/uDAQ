
# UDQ Next Sprint Plan — Runtime Diagnostics and Evidence Coherence

**Status:** planned future work only — not started in this package.

## Objective
Turn the successful Sprint 1 and Sprint 2 proof lines into a coherent platform-level runtime truth surface.

## Why this is next
- the shell/controller concentration risk has already been reduced
- the bounded real-U6 line now provides a real hardware specimen with demonstrated startup, disconnect handling, and same-run recovery
- the package is about to be folded into formal project-management workflows, which increases the value of clean evidence, vocabulary, and review surfaces

## Planned scope
- unified runtime vocabulary across adapter state, runtime phase, UI phase, and review summaries
- clean taxonomy split between runtime events, alarms, operator actions, and diagnostics snapshots
- generalized runtime evidence bundle pattern that can host device-specific snapshots cleanly
- audience-layered metrics for reviewer/operator, engineering, and internal performance uses
- PM/reviewer-facing rollups derived from the same canonical evidence source

## Out of scope
- new hardware families
- historian/export redesign
- broad UI redesign
- major architecture rewrite
- generalized observability platform buildout beyond the bounded slice

## Exit condition for starting this sprint
First complete the final documentation update and external-review alignment pass so the package truth surfaces fully match the current proof state.
