from __future__ import annotations

from dataclasses import dataclass

from universaldaq.outputs import CommandTrace
from universaldaq.profiles import RestoreResult
from universaldaq.ui import AuthoritySurface, GraphModeSession


@dataclass(frozen=True, slots=True, kw_only=True)
class SprintOneModelSlice:
    authority_surface: AuthoritySurface
    graph_session: GraphModeSession
    command_trace: CommandTrace | None = None
    restore_result: RestoreResult | None = None
    last_export_manifest_id: str | None = None
    last_export_summary: str | None = None
    actor_role_label: str | None = None
    granted_capabilities: tuple[str, ...] = ()
