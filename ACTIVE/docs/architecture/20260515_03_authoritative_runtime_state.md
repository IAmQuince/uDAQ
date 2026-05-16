# Authoritative Runtime State — 20260515_03

**Controlled architecture note**  
ID: UDQ-ARCH-NOTE-20260515-03  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture  
Authority: DERIVED

## Package identity
- Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`
- Sprint: `20260515_03_state`

## Purpose
The authoritative runtime state spine gives runtime, diagnostics, review, and UI projection code one inspectable snapshot shape. It is hardware-free, deterministic to serialize, and side-effect-free to build.

## Public entry points
- `universaldaq.runtime.build_authoritative_runtime_snapshot(...)`
- `universaldaq.runtime.RuntimeStateSnapshot.build(...)`
- `universaldaq.runtime.RuntimeStateService.build_snapshot(...)`
- `RuntimeStateSnapshot.to_dict()` for JSON-compatible output

## Requested, applied, and observed semantics
Requested, applied, and observed are separate truth records.

- `requested_state` records operator intent, draft/proposal/preflight state, or review posture.
- `applied_state` records only authoritative runtime state that has actually been published as applied.
- `observed_state` records readback/evidence. It is not a request and does not imply an apply.

Future live mapping or command sprints must attach to these channels without merging them into one status field.

## Sandbox vs authoritative boundary
Sprint 1 sandbox mapping state can be projected into the snapshot only as sandbox/draft/proposal/preflight/review/prepared-request/diagnostic requested state. Sandbox projection uses `RuntimeAuthorityZone.SANDBOX`, sets `authoritative_applied` to false, and leaves mapping `applied_state` and `observed_state` empty.

This sprint does not promote sandbox state into live mapping, hardware configuration, output permission, command authority, or runtime mutation proof.

## Degraded, stale, unavailable, and simulated vocabulary
The snapshot carries explicit aggregate records for:

- `stale_state`
- `unavailable_state`
- `degraded_state`
- `simulated_state`

Devices, points, signals, and variables also carry local availability/posture fields plus last-update and data-age fields where available.

## Extension guidance
- GPT-5.4 should write contract/governance tests against the public entry points, not private helper functions.
- Codex 5.3 should build CLI/JSON diagnostics by calling `build_authoritative_runtime_snapshot(...)` or `RuntimeStateService.build_snapshot(...)` and serializing `to_dict()`.
- UI/review surfaces should read the snapshot as projection input; UI state remains separate from machine truth.

## Explicitly deferred
- live mapping apply
- hardware writes
- production command authority
- physical output authority
- production historian behavior
- runtime logic deployment
- vendor-specific behavior in the universal core
