from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkspaceTaskMap:
    workspace_id: str
    primary_goal: str
    primary_surface: str
    graph_mode_default: str
    secondary_surfaces: tuple[str, ...]
    persistent_status: tuple[str, ...]
    hidden_or_contextual: tuple[str, ...]


def default_workspace_task_maps() -> tuple[WorkspaceTaskMap, ...]:
    return (
        WorkspaceTaskMap(
            workspace_id='operate',
            primary_goal='monitor signals and execute guarded control actions',
            primary_surface='live graph and active signal summary',
            graph_mode_default='primary',
            secondary_surfaces=('explorers', 'trace inspector', 'events console', 'control column'),
            persistent_status=('runtime posture', 'device/session', 'selected signal freshness', 'alarm summary', 'graph mode'),
            hidden_or_contextual=('mapping drafts', 'logic palette', 'deep capability details'),
        ),
        WorkspaceTaskMap(
            workspace_id='logic_designer',
            primary_goal='author and inspect logic relationships',
            primary_surface='logic canvas',
            graph_mode_default='compact_pip',
            secondary_surfaces=('signal explorer', 'logic inspector', 'PiP graph', 'events console'),
            persistent_status=('runtime posture', 'graph mode', 'selected signal freshness', 'mapping authority state'),
            hidden_or_contextual=('full graph chrome', 'deep session notes', 'device onboarding controls'),
        ),
        WorkspaceTaskMap(
            workspace_id='system',
            primary_goal='inspect devices, capability evidence, and mapping drafts',
            primary_surface='device and mapping surfaces',
            graph_mode_default='compact_pip',
            secondary_surfaces=('device explorer', 'capability summary', 'PiP graph', 'events console'),
            persistent_status=('runtime posture', 'capability mode', 'read/write state', 'limited-access reason', 'mapping draft state'),
            hidden_or_contextual=('full graph chrome', 'trace styling controls'),
        ),
        WorkspaceTaskMap(
            workspace_id='session_review',
            primary_goal='review recent activity and historical context',
            primary_surface='session review detail',
            graph_mode_default='primary',
            secondary_surfaces=('review graph overlay', 'notes', 'events console'),
            persistent_status=('runtime posture', 'graph mode', 'selected signal freshness', 'recent event count'),
            hidden_or_contextual=('mapping editor', 'control authoring controls'),
        ),
    )


def workspace_task_map_by_id() -> dict[str, WorkspaceTaskMap]:
    return {item.workspace_id: item for item in default_workspace_task_maps()}
