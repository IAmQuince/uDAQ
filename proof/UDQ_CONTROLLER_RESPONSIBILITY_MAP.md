# UDQ Controller Responsibility Map

## Controller retained responsibilities
- shell session ownership
- authorization decision recording
- shell evidence shaping
- lifecycle transition metric updates
- command-record append spine
- recent review-summary helper views
- delegation to bounded handlers

## Extracted responsibilities
### workspace_profile_handler
- navigation
- trace visibility
- overlays
- graph-mode transitions
- history-range selection
- save/autosave/last-session checkpoints
- restore-profile rebuild flow

### command_export_handler
- output request submission
- alarm assertion / acknowledgment / return-to-normal
- dry-run adapter command admission
- export-intent construction
- export policy evaluation and bundle assembly
- adapter handoff for admitted output requests

### automation_review_handler
- rule registration
- sequence registration
- sequence start
- automation evaluation
- automation claim/suppression logic
- lifecycle review bundle assembly
