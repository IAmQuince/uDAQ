from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from universaldaq.common import EventTime, SignalId
from universaldaq.signals import BindingPolicy, VariableDefinition

from .first_signal import FirstSignalPlanner

if TYPE_CHECKING:
    from .controller import ShellActionResult, ShellController


@dataclass(slots=True)
class ShellBindingVariableHandler:
    controller: 'ShellController'

    def bind_logical_signal_to_point(
        self,
        *,
        logical_signal_id: SignalId,
        point_key: str,
        display_name: str | None = None,
        binding_policy: BindingPolicy = BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
        timestamp: EventTime,
    ) -> 'ShellActionResult':
        binding_summary = self.controller._lifecycle().bind_logical_signal(
            logical_signal_id=logical_signal_id,
            point_key=point_key,
            display_name=display_name,
            binding_policy=binding_policy,
        )
        first_signal_summary = FirstSignalPlanner.build_summary(
            services=self.controller.services,
            device=self.controller.session.ui_session.active_device,
            previous_summary=self.controller.session.ui_session.first_signal_summary,
            preferred_signal_id=logical_signal_id,
            lifecycle_phase=self.controller.session.ui_session.device_lifecycle_phase,
            auto_bound=False,
        )
        ui_session = self.controller._ui_session_with_lifecycle_update(
            binding_review_summary=binding_summary,
            first_signal_summary=first_signal_summary,
        )
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='BIND',
            summary='logical signal bound to projected point',
            attributes={'logical_signal_id': str(logical_signal_id), 'point_key': point_key},
        )
        return self.controller._commit_with_ui_session('bind_logical_signal_to_point', ui_session=ui_session, evidence=evidence)

    def register_variable_definition(self, *, definition: VariableDefinition, timestamp: EventTime) -> 'ShellActionResult':
        variable_summary = self.controller._lifecycle().register_variable_definition(definition=definition, timestamp=timestamp)
        ui_session = self.controller._ui_session_with_lifecycle_update(variable_health_summary=variable_summary)
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='VARDEF',
            summary='variable definition registered',
            attributes={'variable_id': str(definition.variable_id), 'source_kind': definition.source_kind.value},
        )
        return self.controller._commit_with_ui_session('register_variable_definition', ui_session=ui_session, evidence=evidence)

    def evaluate_variables(self, *, timestamp: EventTime) -> 'ShellActionResult':
        variable_summary = self.controller._lifecycle().evaluate_variables(timestamp=timestamp)
        ui_session = self.controller._ui_session_with_lifecycle_update(variable_health_summary=variable_summary)
        evidence = self.controller._shell_evidence(
            timestamp=timestamp,
            suffix='VAREVAL',
            summary='variable evaluation completed',
            attributes={'variable_count': str(variable_summary.total_variable_count), 'impacted_count': str(variable_summary.impacted_count)},
        )
        return self.controller._commit_with_ui_session('evaluate_variables', ui_session=ui_session, evidence=evidence)
