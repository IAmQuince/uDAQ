# Mapping Apply Preflight and Review Path — 20260330_09

**Controlled architecture note**  
ID: UDQ-ARCH-NOTE-20260330-09  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture  
Authority: DERIVED

## Package identity
- Package ID: `UDQ-PKG-20260330-CONTROLLED-MAPPING-APPLY-PREFLIGHT-AND-REVIEW-PATH-R01`

## Purpose
This note describes the preflight/review layer introduced between shell draft edits and any future controller-authorized mapping apply operation.

## State model
The mapping workflow now separates:
1. backend/controller authoritative readback;
2. shell-local draft rows;
3. structured mapping-change proposals;
4. preflight results;
5. operator review summaries;
6. dry-run / prepared-only apply request artifacts.

## Non-execution guarantee
`MappingApplyRequest.executed` is always false in this sprint. `prepare_mapping_apply_request` accepts only `DRY_RUN` and `PREPARED_ONLY` modes. A live execution mode is intentionally unavailable.

## Preflight controls
Preflight blocks request preparation when authoritative readback is unavailable, a readback timestamp is missing, a required endpoint or logical ID is missing, an authoritative row reports stale/conflict/unavailable, a logical target is unknown, or a proposed endpoint is not in the known discovered endpoint set when such a set is supplied.

Warnings are preserved for review when the proposal remains structurally safe but should be noticed by the operator, such as unit changes.

## Authority boundary
The shell may draft and request review. It does not own applied state. Backend/controller readback remains the basis for every prepared request, and the request carries the readback timestamp used for the review.

## Deferred work
Future work may add a controller-authorized commit boundary. That future work must preserve the review artifact, require confirmation, and continue to reject stale readback before any authoritative mutation occurs.
