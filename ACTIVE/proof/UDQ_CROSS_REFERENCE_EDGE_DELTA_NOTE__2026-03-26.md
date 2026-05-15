# Cross-Reference Edge Delta Note - 2026-03-26

## Question
Why did the active cross-reference graph contract from the earlier 636-edge posture to the current 527-edge posture without triggering a structural failure?

## Answer
The active graph reduction is treated as an intentional cleanup outcome rather than silent traceability loss. The current active registry still passes the dimensions that matter operationally:
- `depends_on` relationships resolve
- active rows participate in the graph
- self-references are zero
- duplicates are zero
- filename-to-document identity checks pass
- document completeness gate passes

The reduction therefore reflects cleanup of obsolete, duplicate, or previously over-counted edges across the evolving documentation set, not a collapse of the authoritative dependency model. The right correction was explanatory visibility, not a forced edge-count increase.

## Release-surface action
This note is now carried into the release-facing story so reviewers no longer have to infer intent from raw counts alone.
