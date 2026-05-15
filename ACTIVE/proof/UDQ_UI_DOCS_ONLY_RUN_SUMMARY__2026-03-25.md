# UI Docs-Only Run Summary — 2026-03-25

## Run type
Docs-only UI refinement pass.

## What changed
- reframed the UI around **Run / Control / Review / System**
- added a new controlled document for the **Control workspace and control authoring model**
- expanded the shell spec to cover left/right dock persistence, a lower evidence pane, contextual toolbars, and layout presets
- expanded the graph spec to cover live follow, sliding-window live view, whole-history review, explore mode, and truthful return-to-live behavior
- broadened the old rules-editor concept into a structured-first **control authoring** concept
- preserved **sequence convenience** as a supporting feature for timed steps, output/setpoint profiles, and internal/virtual variable changes
- corrected the Genesys inventory document so it now functions as a preservation map rather than an architecture driver
- updated the requirements matrix and gap report so the UI refinement is reflected at the package summary level

## Sequence refinement captured
The Sequence subtab remains intentionally preserved for convenient procedural control of:
- external outputs
- setpoints
- internal or virtual variables
- timed steps, waits, ramps, and profiles

The docs now state clearly that sequence authoring is important but is **not** the only control-authoring metaphor.

## What did not change
- no code was changed
- no backend contracts were widened
- no actuation claims were added
- no runtime completeness claims were widened

## Reviewer focus
Reviewers should look for:
- coherence across doctrine, architecture, shell, workspaces, control authoring, graph behavior, and requirements summary
- preservation of sequence convenience without UI overreach
- no accidental device-specific or domain-specific bake-in
