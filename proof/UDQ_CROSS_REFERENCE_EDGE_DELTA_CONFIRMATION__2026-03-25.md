# UniversalDAQ — Cross-Reference Edge Delta Confirmation — 2026-03-25

## Question from review
The external review noted that cross-reference edges dropped from 636 to 527 and asked for confirmation that this was intentional rather than accidental edge loss.

## Result
The change was intentional cleanup.

## Findings
- prior registry (`r16`) contained 636 rows but only 413 distinct `(source_document_id, target_document_id, edge_type)` relationships
- the current registry (`r17`) contains 527 rows and 527 distinct relationships
- duplicate/stale repeated edges were removed entirely
- the distinct relationship set did **not** shrink; it grew by 114 distinct edges relative to the older registry, including ADR links and newly normalized active-doc relationships
- no canonical relationship class was found to have been accidentally removed in the cleanup pass

## Conclusion
The 636 -> 527 change reflects deduplication and normalization, not accidental relationship loss.
