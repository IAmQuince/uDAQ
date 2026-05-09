# Cross-Device Tag and Acquisition Spine — Architecture Note

Status: ACTIVE

## Purpose

Start the **read-side simultaneous multi-device architecture** without destabilizing the stabilized historian/recovery baseline.

## Scope of this slice

This slice adds:
- canonical cross-device tag definitions
- a bounded multi-adapter acquisition broker
- mixed-source read-side ingestion into the existing runtime evidence lane
- mixed-source derived-variable proof in the control environment
- acceptance/report artifacts for simultaneous ingest

This slice does **not** add:
- cross-device output routing
- command arbitration
- fail-safe write ownership
- broad UI authoring surfaces
- broad hardware-family generalization claims

## Core architectural rule

The universal core does not speak in vendor terms.

The core speaks in:
- canonical tags
- normalized samples
- normalized runtime events
- generic adapter health/status

Vendor-native details remain inside support-pack adapters and discovery providers.
