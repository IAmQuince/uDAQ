# Authoritative Binding Readback Notes — 20260330_08

Document ID: UDQ-ARCH-NOTE-20260330-08
Revision: r0
Status: Active implementation note
Package: UDQ-PKG-20260330-CONTROLLER-BACKED-AUTHORITATIVE-MAPPING-READBACK-AND-DESKTOP-FIX-CLOSURE-R01

## Purpose

The shell needs a trustworthy way to display applied mapping state before it is allowed to apply mapping changes. This sprint adds the readback side of that boundary.

## State separation

The mapping workflow now distinguishes three layers:

1. Discovered I/O — raw device/adaptor points projected by the runtime.
2. Draft mapping — shell-local operator edits that are explicitly non-authoritative.
3. Applied authoritative mapping — backend/controller binding state exposed through readback.

## Readback seam

`BackendBindingReadbackProvider` exposes backend-owned binding state as an `AuthoritativeBindingInventory`. This provider is read-only by design. Future apply behavior must use a separate controlled command path with authorization, dry-run/review semantics, and safe-state protections.

## Shell classification vocabulary

The shell-facing Device I/O model recognizes these authority states:

- `applied`: draft/display row matches backend-applied binding readback.
- `draft`: a shell-local mapping exists but backend readback has not applied it.
- `modified`: shell-local draft differs from backend-applied readback.
- `stale`: backend readback points to stale/disabled projected point inventory.
- `conflict`: backend readback resolves to the wrong device identity.
- `unavailable`: no backend-applied binding or no usable projected point is available.

## Deferred

This sprint does not implement controller-backed apply, live hardware authority verification, or runtime logic deployment.
