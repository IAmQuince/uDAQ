# UniversalDAQ — Public API Freeze

**Controlled document**  
ID: UDQ-README-API-001  
Status: ACTIVE  
Revision: r1  
Owner: Core Architecture  
Authority: PRIMARY  
Source docs: UDQ-IMP-PLAN-001, UDQ-GOV-WI-001

## Purpose
This file freezes the bounded public Python surface that future sprints may build on without accidental interface drift.

## Compatibility rule
Treat the symbols listed here as the current public surface.
Refactors may change internals, but they shall not silently rename, remove, or repurpose these exports without updating this file, the release notes, and the dependency review ledger.

## Public surface by package
### `universaldaq.app`
- `AUTOSAVE_PROFILE_ID`
- `BootstrappedShell`
- `LAST_SESSION_PROFILE_ID`
- `ShellActionResult`
- `ShellBootstrapper`
- `ShellController`
- `ShellServiceRegistry`
- `ShellSession`
- `SprintOneModelSlice`
- `build_default_service_registry`

### `universaldaq.signals`
- `DerivedEvaluationResult`
- `DerivedSignalDefinition`
- `SignalDefinition`
- `SignalRegistry`
- `SignalSnapshot`
- `dependency_graph`
- `find_cycles`
- `validate_derived_signals`
- `validate_for_activation`

### `universaldaq.outputs`
- `ArbitrationOutcome`
- `CommandTrace`
- `CommandTraceFactory`
- `OutputAppliedState`
- `OutputArbiter`
- `OutputCommandService`
- `OutputComparison`
- `OutputObservedState`
- `OutputRequest`
- `validate_command_trace`

### `universaldaq.events`
- `AlarmLifecycle`
- `AlarmLifecycleService`
- `AlarmTransition`

### `universaldaq.profiles`
- `FileProfileStore`
- `InMemoryProfileStore`
- `ProfileSnapshot`
- `RestorePlan`
- `RestorePlanner`
- `RestoreResult`
- `WorkspaceState`
- `deserialize_profile_snapshot`
- `deserialize_workspace_state`
- `serialize_profile_snapshot`
- `serialize_workspace_state`

### `universaldaq.historian`
- `ArtifactDescriptor`
- `ArtifactManifest`
- `BundleBuildResult`
- `BundleIntegrityWarning`
- `BundleInventory`
- `EvidenceBundle`
- `EvidenceBundleService`
- `ExportIntent`
- `ExportScope`
- `ManifestSummary`
- `ProofBundleSummary`
- `ReviewArtifact`
- `SerializedArtifact`
- `build_bundle_inventory`
- `summarize_bundle`
- `summarize_manifest`

### `universaldaq.ui`
- `AuthoritySurface`
- `GraphModeSession`
- `GraphPanelViewModel`
- `ShellViewModel`
- `ShellViewModelBuilder`
- `UISessionFactory`
- `UISessionState`

## Explicitly internal for now
The following remain implementation detail surfaces and are not frozen as public contracts in this package:
- submodule-private helpers not re-exported through package `__all__`
- reserved later-slice packages such as `backend`, `remote`, `rules`, `sequences`, and `diagnostics`; `security` and `adapters` are now active bounded slices
- generated registries and snapshots as implementation artifacts rather than runtime APIs

## Stability notes
- The public surface is intentionally small and centered on shell/service composition and pure models.
- The controller layer was added additively; the older bootstrap/service entry points remain valid.
- Any removal or signature break should be treated as a governed compatibility change.
