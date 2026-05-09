# UniversalDAQ — Vertical Slice Summary (2026-03-23)

## Sprint intent
Advance the package from a hardened lifecycle/binding foundation into a real shell-visible vertical slice that exercises the workflow end to end.

## Delivered slice
- discover device
- activate device
- project adapter capability into durable point definitions
- bind logical signals to projected points
- evaluate variables from live signal snapshots
- degrade affected logic on disconnect
- recover and republish on reconnect
- expose review state through shell view models and a machine-readable lifecycle review bundle

## Core implementation changes
- added `ShellLifecycleOrchestrator` to coordinate lifecycle, projection, binding review, variable health, reconciliation summaries, and workbench surfaces
- added explicit UI/session/view-model review summaries for lifecycle, bindings, variables, reconciliation, and workbench availability
- added point-definition replacement semantics and binding-review auto-rebind logic for stable logical identities across reprojected point inventories
- added lifecycle-aware signal publication and variable evaluation in quick-start, disconnect, reconnect, and active-device poll flows
- added a reusable diagnostic harness: `python -m tools.diagnostics.dump_lifecycle_review_bundle --output <path>`

## Bounded specimen deepening
- deepened the optional LabJack U6 support pack metadata with richer channel-family and review-surface hints
- preserved the vendor boundary: all LabJack specifics remain in `universaldaq_labjack`, not in the universal core package

## Proof added
- new scenario proof for end-to-end binding/variable/disconnect/reconnect lifecycle behavior
- new integration proof for lifecycle review bundle content and workbench surfacing
- new contract proof for auto-rebinding to reprojected point inventories under the same stable device identity
- updated pytest evidence log and lifecycle bundle proof under `proof/logs/`

## Exit state
The package now has a truthful shell-visible lifecycle/review slice and is ready for the next sprint to deepen first-party bridge realism and bounded interactive review authoring.
