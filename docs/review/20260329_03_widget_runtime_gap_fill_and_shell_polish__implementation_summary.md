# 20260329_03 Widget Runtime Gap-Fill and Shell Polish

## Intent

Close the gap between the shell geometry and graph-presentation policy work and the actual widget-runtime behavior, while keeping backend/runtime truth isolated from the visible shell.

## What changed

- Replaced the outer dock-dominant shell composition with a splitter-first runtime shell structure:
  - horizontal outer splitter for explorer / center / control column
  - vertical center splitter for workspace / events
- Hardened runtime window geometry restore around the existing layout-state policy and moved the shell to layout schema version 3.
- Added bounded graph overlay behavior for non-Operate workspaces so Logic Designer and System can run with a compact or enlarged graph overlay instead of a permanently dominant full graph.
- Added persisted graph presentation state and bounded PiP geometry state to shell settings and saved-view payloads.
- Surfaced capability evidence more explicitly in the shell session panel and diagnostics export:
  - capability mode
  - identity state
  - read state
  - write state
  - limited-access reason
- Preserved mapping authority boundaries by keeping the mapping surface explicitly draft/preview only.
- Added task-first workspace design inventory and associated smoke/contract coverage.

## Honest limits

- The widget-runtime changes compile and are covered by non-GUI tests, but they were not bench-verified in this environment because PySide6 and pyqtgraph are not installed here.
- Session Review now participates in graph-mode policy through the overlay path, but the main primary graph surface is still most mature in Operate.

## Reviewer focus for the next local bench run

1. Verify left / center / right splitters now resize meaningfully.
2. Verify the events panel stays only under the center region.
3. Verify Logic Designer and System show the graph as an overlay instead of consuming the whole workspace.
4. Verify overlay drag/resize stays bounded.
5. Verify window launch/restore no longer drifts off-screen.
6. Verify capability evidence is readable from the live-device session panel.
7. Verify Mapping Draft wording cannot be confused with applied runtime truth.
