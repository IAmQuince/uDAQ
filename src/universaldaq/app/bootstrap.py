from __future__ import annotations

from dataclasses import dataclass

from universaldaq.common import EventTime, RestoreOrigin
from universaldaq.profiles import BenchPersistenceState, ProfileSnapshot, RestorePlan, RestorePlanner
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession
from universaldaq.ui.session_state import UISessionFactory

from .models import SprintOneModelSlice
from .service_registry import ShellServiceRegistry, build_default_service_registry
from .session import ShellSession


@dataclass(frozen=True, slots=True, kw_only=True)
class BootstrappedShell:
    model_slice: SprintOneModelSlice
    session: ShellSession
    services: ShellServiceRegistry


class ShellBootstrapper:

    @staticmethod
    def bootstrap_from_bench_state(
        *,
        bench_state: BenchPersistenceState,
        authority_surface: AuthoritySurface,
        graph_session: GraphModeSession,
        timestamp: EventTime,
        services: ShellServiceRegistry | None = None,
        actor_context: ActorContext | None = None,
    ) -> BootstrappedShell:
        boot = ShellBootstrapper.bootstrap_from_profile(
            profile_snapshot=bench_state.profile_snapshot,
            authority_surface=authority_surface,
            graph_session=graph_session,
            timestamp=timestamp,
            restore_origin=RestoreOrigin.SESSION,
            services=services,
            actor_context=actor_context,
        )
        summary = bench_state.historical_summary
        ui_session = boot.session.ui_session.with_persistence_context(
            preferred_adapter_id=bench_state.preferred_adapter_id or '',
            preferred_device_key=bench_state.preferred_device_key or '',
            preferred_channel_key=bench_state.preferred_channel_key or '',
            restored_historical_context_label='restored context remains historical until a live reconnect occurs',
            last_session_summary_id=None if summary is None else summary.summary_id,
            last_session_summary_label=None if summary is None else (summary.last_signal_display_name or summary.preferred_channel_key or 'last session'),
            session_note_count=0 if summary is None else len(summary.operator_notes),
            pending_note_draft=bench_state.pending_note_draft,
        )
        session = boot.session.with_ui_session(ui_session)
        if summary is not None:
            session = session.with_persisted_session_summary(summary)
            for note in summary.operator_notes:
                session = session.append_operator_note(note)
        return BootstrappedShell(model_slice=boot.model_slice, session=session, services=boot.services)
    @staticmethod
    def bootstrap_from_profile(
        *,
        profile_snapshot: ProfileSnapshot,
        authority_surface: AuthoritySurface,
        graph_session: GraphModeSession,
        timestamp: EventTime,
        restore_origin: RestoreOrigin = RestoreOrigin.PROFILE,
        services: ShellServiceRegistry | None = None,
        actor_context: ActorContext | None = None,
    ) -> BootstrappedShell:
        restore_result = RestorePlanner.apply(
            RestorePlan(
                snapshot=profile_snapshot,
                origin=restore_origin,
                machine_write_intent=False,
            ),
            timestamp=timestamp,
        )
        service_registry = services or build_default_service_registry()
        resolved_actor_context = actor_context or ActorContext(
            actor_id='shell-user',
            role_class=RoleClass.OPERATOR,
            origin='local-shell',
            is_local=True,
        )
        resolved_actor_context = resolved_actor_context.with_session(f'SESSION-{profile_snapshot.profile_id}-{int(timestamp)}')
        granted_permission_families = service_registry.security.permissions_for_actor(resolved_actor_context)
        ui_session = UISessionFactory.from_restore(
            restore_result=restore_result,
            authority_surface=authority_surface,
            graph_session=graph_session,
            actor_role_label=resolved_actor_context.role_label,
            granted_capabilities=granted_permission_families,
        )
        session = ShellSession(
            session_id=resolved_actor_context.session_id or f'SESSION-{profile_snapshot.profile_id}-{int(timestamp)}',
            profile_snapshot=profile_snapshot,
            restore_result=restore_result,
            ui_session=ui_session,
            actor_context=resolved_actor_context,
            granted_permission_families=granted_permission_families,
        )
        service_registry.runtime_quality.activate_session(session_id=session.session_id)
        service_registry.runtime_quality.write_checkpoint(
            timestamp=timestamp,
            payload={
                'bootstrap': {
                    'profile_id': str(profile_snapshot.profile_id),
                    'restore_origin': restore_origin.value,
                    'page': ui_session.page,
                    'graph_mode': ui_session.graph_session.mode.value,
                    'actor_id': str(resolved_actor_context.actor_id),
                }
            },
        )
        model_slice = SprintOneModelSlice(
            authority_surface=authority_surface,
            graph_session=graph_session,
            restore_result=restore_result,
            actor_role_label=resolved_actor_context.role_label,
            granted_capabilities=granted_permission_families,
        )
        service_registry.profiles.save(profile_snapshot)
        return BootstrappedShell(model_slice=model_slice, session=session, services=service_registry)
