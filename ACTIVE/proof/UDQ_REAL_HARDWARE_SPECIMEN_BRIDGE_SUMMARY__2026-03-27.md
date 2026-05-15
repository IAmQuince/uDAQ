# UniversalDAQ Real-Hardware Specimen Bridge Summary — 2026-03-27

## Intent
Open the next bounded code section without destabilizing the now-repeatable simulated historian/recovery lane.

## Closure rule
- simulated evidence acceptance must remain green
- the real-hardware bridge must keep the same one-command entry surface
- hardware absence must be reported explicitly as `SKIP`
- hardware presence must populate the same evidence/review surface without silently changing the core runtime contract

## Expected operator behavior
Run the usual evidence acceptance command.
The acceptance bundle now includes a real-hardware bridge subsection with one of two honest outcomes:
- `PASS` — bounded real-U6 specimen path completed and produced reviewable artifacts
- `SKIP` — no usable real U6 was present, but the package remained truthful and bounded
