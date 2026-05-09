# Implementation Summary — UI Architecture Documentation Update

**CANONICAL CURRENT SUPPORTING LEDGER FOR PACKAGE `UDQ-PKG-20260328-UI-ARCHITECTURE-DOCUMENTATION-UPDATE-R01`**

## What landed
- reframed the primary workspaces as Operate, Logic Designer, Session Review, and System
- locked the shell docking doctrine so the primary control column is dockable left or right and defaults to the right
- formalized Device Explorer versus Signal Explorer versus Logic Module Explorer
- documented the requirement that any plottable signal may be graphed through curated browse lenses
- documented SignalRef / TraceBinding / TracePresentation separation
- documented trace-style flexibility, interactive legend behavior, alarm-severity overlays, and saved graph setups
- documented autosave as a toggleable setting and required in-app save/load/edit of settings and profiles
- documented pyqtgraph retention as the graph engine while reserving application-owned multiresolution and rendering discipline
- reframed the control-authoring surface as a dedicated Logic Designer workspace inside the same shell rather than a mixed live-operation surface

## Important boundaries
- this pass is docs-only; it does not claim a finished visible GUI window or a delivered widget implementation of the new shell
- the pass reserves UI information architecture, persistence, and performance doctrine so later GUI work does not invent those rules ad hoc
