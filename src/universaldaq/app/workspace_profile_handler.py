from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from universaldaq.common import EventTime, GraphMode, ProfileId, RestoreOrigin, TraceId
from universaldaq.profiles import ProfileSnapshot, RestorePlan, RestorePlanner
from universaldaq.ui.session_state import UISessionFactory

if TYPE_CHECKING:
    from .controller import ShellActionResult, ShellController


@dataclass(slots=True)
class ShellWorkspaceProfileHandler:
    controller: 'ShellController'

    def navigate(self, *, page: str, timestamp: EventTime) -> 'ShellActionResult':
        ui_session = self.controller.session.ui_session.with_workspace_state(self.controller._workspace_from_current(page=page))
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='PAGE',
            summary='workspace page selected',
            attributes={'page': page},
        )
        return self.controller._commit('navigate', self.controller.session.with_ui_session(ui_session).append_shell_evidence(evidence))

    def set_trace_visibility(self, *, trace_id: TraceId, visible: bool, timestamp: EventTime) -> 'ShellActionResult':
        traces = list(self.controller.session.ui_session.workspace_state.visible_traces)
        if visible and trace_id not in traces:
            traces.append(trace_id)
        if not visible:
            traces = [item for item in traces if item != trace_id]
        ui_session = self.controller.session.ui_session.with_workspace_state(self.controller._workspace_from_current(visible_traces=tuple(traces)))
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='TRACE',
            summary='trace visibility changed',
            attributes={'trace_id': str(trace_id), 'visible': str(visible).lower()},
        )
        return self.controller._commit('set_trace_visibility', self.controller.session.with_ui_session(ui_session).append_shell_evidence(evidence))

    def set_overlay(self, *, overlay_name: str, visible: bool, timestamp: EventTime) -> 'ShellActionResult':
        overlays = list(self.controller.session.ui_session.overlays)
        if visible and overlay_name not in overlays:
            overlays.append(overlay_name)
        if not visible:
            overlays = [item for item in overlays if item != overlay_name]
        ui_session = self.controller.session.ui_session.with_overlays(tuple(overlays))
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='OVERLAY',
            summary='graph overlay visibility changed',
            attributes={'overlay': overlay_name, 'visible': str(visible).lower()},
        )
        return self.controller._commit('set_overlay', self.controller.session.with_ui_session(ui_session).append_shell_evidence(evidence))

    def select_history_range(self, *, start: EventTime, end: EventTime, timestamp: EventTime) -> 'ShellActionResult':
        graph_session = self.controller.session.ui_session.graph_session.transition(
            GraphMode.HISTORY,
            timestamp,
            summary='history range explored',
            attributes={'range_start': str(start), 'range_end': str(end)},
        )
        ui_session = (
            self.controller.session.ui_session
            .with_graph_session(graph_session)
            .with_workspace_state(self.controller._workspace_from_current(review_mode=graph_session.mode))
            .with_selected_range((start, end))
        )
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='RANGE',
            summary='history range selected',
            attributes={'range_start': str(start), 'range_end': str(end)},
        )
        return self.controller._commit('select_history_range', self.controller.session.with_ui_session(ui_session).append_shell_evidence(evidence))

    def switch_graph_mode(self, *, mode: GraphMode, timestamp: EventTime) -> 'ShellActionResult':
        graph_session = self.controller.session.ui_session.graph_session.transition(mode, timestamp)
        selected_range = None if mode == GraphMode.LIVE else self.controller.session.ui_session.selected_range
        ui_session = (
            self.controller.session.ui_session
            .with_graph_session(graph_session)
            .with_workspace_state(self.controller._workspace_from_current(review_mode=graph_session.mode))
            .with_selected_range(selected_range)
        )
        return self.controller._commit('switch_graph_mode', self.controller.session.with_ui_session(ui_session))

    def return_to_live(self, *, timestamp: EventTime) -> 'ShellActionResult':
        previous_mode = self.controller.session.ui_session.graph_session.mode.value
        graph_session = self.controller.session.ui_session.graph_session.return_to_live(timestamp)
        ui_session = (
            self.controller.session.ui_session
            .with_graph_session(graph_session)
            .with_workspace_state(self.controller._workspace_from_current(review_mode=graph_session.mode))
            .with_selected_range(None)
        )
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='LIVE',
            summary='return to live invoked',
            attributes={'previous_mode': previous_mode},
        )
        return self.controller._commit('return_to_live', self.controller.session.with_ui_session(ui_session).append_shell_evidence(evidence))

    def save_profile(self, *, profile_id: ProfileId, timestamp: EventTime) -> 'ShellActionResult':
        snapshot = ProfileSnapshot(profile_id=profile_id, workspace_state=self.controller.session.ui_session.workspace_state)
        self.controller.services.profiles.save(snapshot)
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='PROFILESAVE',
            summary='profile snapshot saved',
            attributes={'profile_id': str(profile_id)},
        )
        return self.controller._commit('save_profile', self.controller.session.append_shell_evidence(evidence))

    def save_autosave(self, *, timestamp: EventTime) -> 'ShellActionResult':
        snapshot = ProfileSnapshot(profile_id=self.controller.AUTOSAVE_PROFILE_ID, workspace_state=self.controller.session.ui_session.workspace_state)
        self.controller.services.profiles.save(snapshot)
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='AUTOSAVE',
            summary='autosave snapshot saved',
            attributes={'profile_id': str(self.controller.AUTOSAVE_PROFILE_ID), 'origin': RestoreOrigin.AUTOSAVE.value},
        )
        return self.controller._commit('save_autosave', self.controller.session.append_shell_evidence(evidence))

    def save_last_session(self, *, timestamp: EventTime) -> 'ShellActionResult':
        snapshot = ProfileSnapshot(profile_id=self.controller.LAST_SESSION_PROFILE_ID, workspace_state=self.controller.session.ui_session.workspace_state)
        self.controller.services.profiles.save(snapshot)
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='SESSIONSAVE',
            summary='last-session snapshot saved',
            attributes={'profile_id': str(self.controller.LAST_SESSION_PROFILE_ID), 'origin': RestoreOrigin.SESSION.value},
        )
        return self.controller._commit('save_last_session', self.controller.session.append_shell_evidence(evidence))

    def restore_profile(self, *, profile_id: ProfileId, origin: RestoreOrigin, timestamp: EventTime) -> 'ShellActionResult':
        snapshot = self.controller.services.profiles.load(profile_id)
        restore_result = RestorePlanner.apply(
            RestorePlan(snapshot=snapshot, origin=origin, machine_write_intent=False),
            timestamp=timestamp,
        )
        graph_session = self.controller.session.ui_session.graph_session.transition(
            restore_result.restored_workspace.review_mode,
            timestamp,
            summary='graph mode aligned to restored workspace',
            attributes={'restore_origin': origin.value},
        )
        ui_session = UISessionFactory.from_restore(
            restore_result=restore_result,
            authority_surface=self.controller.session.ui_session.authority_surface,
            graph_session=graph_session,
            actor_role_label=self.controller.session.actor_context.role_label,
            granted_capabilities=self.controller.session.granted_permission_families,
        )
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='RESTORE',
            summary='workspace restored into shell session',
            attributes={'profile_id': str(profile_id), 'origin': origin.value, 'machine_write_intent': 'false'},
        )
        session = self.controller.session.with_profile_snapshot(snapshot).with_restore_result(restore_result).with_ui_session(ui_session).append_shell_evidence(evidence)
        return self.controller._commit('restore_profile', session)
