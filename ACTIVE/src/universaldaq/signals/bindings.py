from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping

from universaldaq.adapters import AdapterPointRef
from universaldaq.common import OutputId, RuntimeMetricsStore, SignalId


class BindingPolicy(StrEnum):
    STRICT_IDENTITY = 'strict_identity'
    SAME_DEVICE_SAME_POINT = 'same_device_same_point'
    AUTO_REBIND_IF_CONFIDENT = 'auto_rebind_if_confident'
    MANUAL_REVIEW_REQUIRED = 'manual_review_required'


class BindingResolutionStatus(StrEnum):
    RESOLVED = 'resolved'
    AUTO_REBOUND = 'auto_rebound'
    MANUAL_REVIEW_REQUIRED = 'manual_review_required'
    UNRESOLVED = 'unresolved'
    BLOCKED_BY_POLICY = 'blocked_by_policy'


@dataclass(frozen=True, slots=True, kw_only=True)
class DevicePointDefinition:
    point_ref: AdapterPointRef
    device_identity_key: str
    friendly_name: str
    role: str
    enabled: bool = True
    metadata: Mapping[str, str] = field(default_factory=dict)

    @property
    def stable_point_key(self) -> str:
        return self.point_ref.stable_key


@dataclass(frozen=True, slots=True, kw_only=True)
class LogicalSignalBinding:
    logical_signal_id: SignalId
    source_point_key: str
    binding_policy: BindingPolicy = BindingPolicy.AUTO_REBIND_IF_CONFIDENT
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class LogicalOutputBinding:
    logical_output_id: OutputId
    target_point_key: str
    binding_policy: BindingPolicy = BindingPolicy.MANUAL_REVIEW_REQUIRED
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class BindingReviewItem:
    binding_kind: str
    logical_id: str
    previous_point_key: str
    resolved_point_key: str | None
    status: BindingResolutionStatus
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class BindingReviewSummary:
    total_signal_binding_count: int = 0
    total_output_binding_count: int = 0
    resolved_signal_count: int = 0
    auto_rebound_signal_count: int = 0
    manual_review_signal_count: int = 0
    unresolved_signal_count: int = 0
    blocked_signal_count: int = 0
    resolved_output_count: int = 0
    unresolved_output_count: int = 0
    items: tuple[BindingReviewItem, ...] = field(default_factory=tuple)

    @property
    def requires_review(self) -> bool:
        return (
            self.manual_review_signal_count > 0
            or self.unresolved_signal_count > 0
            or self.blocked_signal_count > 0
            or self.unresolved_output_count > 0
        )


@dataclass(slots=True)
class SignalBindingService:
    point_definitions: dict[str, DevicePointDefinition] = field(default_factory=dict)
    signal_bindings: dict[SignalId, LogicalSignalBinding] = field(default_factory=dict)
    output_bindings: dict[OutputId, LogicalOutputBinding] = field(default_factory=dict)
    point_definition_signatures: dict[str, tuple[str, ...]] = field(default_factory=dict)
    metrics: RuntimeMetricsStore | None = None

    @staticmethod
    def _definition_signature(definitions: tuple[DevicePointDefinition, ...]) -> tuple[str, ...]:
        rows: list[str] = []
        for definition in definitions:
            metadata = '|'.join(f'{key}={definition.metadata[key]}' for key in sorted(definition.metadata.keys()))
            rows.append(
                '::'.join(
                    (
                        definition.device_identity_key,
                        definition.stable_point_key,
                        definition.friendly_name,
                        definition.role,
                        str(definition.enabled).lower(),
                        metadata,
                    )
                )
            )
        return tuple(sorted(rows))

    @staticmethod
    def _binding_device_identity(metadata: Mapping[str, str], point_key: str) -> str | None:
        value = metadata.get('device_identity_key')
        if value:
            return str(value)
        if '::' in point_key:
            return point_key.split('::', 1)[0]
        return None

    def register_point_definition(self, definition: DevicePointDefinition) -> None:
        self.point_definitions[definition.stable_point_key] = definition
        if self.metrics is not None:
            self.metrics.increment('bindings.point_definition.register.calls')
            self.metrics.set_gauge('bindings.point_definition.count', len(self.point_definitions))

    def replace_device_point_definitions(
        self,
        *,
        device_identity_key: str,
        definitions: tuple[DevicePointDefinition, ...],
    ) -> tuple[DevicePointDefinition, ...]:
        new_signature = self._definition_signature(definitions)
        if self.point_definition_signatures.get(device_identity_key) == new_signature:
            if self.metrics is not None:
                self.metrics.increment('bindings.point_definition.replace.skipped')
                self.metrics.set_gauge('bindings.point_definition.count', len(self.point_definitions))
                self.metrics.set_gauge('bindings.point_definition.last_replace_skipped', 1)
            return definitions

        stale_keys = [
            point_key
            for point_key, definition in self.point_definitions.items()
            if definition.device_identity_key == device_identity_key
        ]
        for point_key in stale_keys:
            self.point_definitions.pop(point_key, None)
        for definition in definitions:
            self.point_definitions[definition.stable_point_key] = definition
        self.point_definition_signatures[device_identity_key] = new_signature
        if self.metrics is not None:
            self.metrics.increment('bindings.point_definition.replace.calls')
            self.metrics.set_gauge('bindings.point_definition.count', len(self.point_definitions))
            self.metrics.set_gauge('bindings.point_definition.last_replace_skipped', 0)
        return definitions

    def point_definitions_for_device(self, device_identity_key: str) -> tuple[DevicePointDefinition, ...]:
        return tuple(
            definition
            for definition in self.point_definitions.values()
            if definition.device_identity_key == device_identity_key and definition.enabled
        )

    def point_keys_for_device(self, device_identity_key: str) -> tuple[str, ...]:
        return tuple(definition.stable_point_key for definition in self.point_definitions_for_device(device_identity_key))

    def bind_signal(self, binding: LogicalSignalBinding) -> None:
        self.signal_bindings[binding.logical_signal_id] = binding
        if self.metrics is not None:
            self.metrics.increment('bindings.signal.bind.calls')
            self.metrics.set_gauge('bindings.signal.count', len(self.signal_bindings))

    def bind_output(self, binding: LogicalOutputBinding) -> None:
        self.output_bindings[binding.logical_output_id] = binding
        if self.metrics is not None:
            self.metrics.increment('bindings.output.bind.calls')
            self.metrics.set_gauge('bindings.output.count', len(self.output_bindings))

    def resolve_signal_source(self, logical_signal_id: SignalId) -> DevicePointDefinition | None:
        binding = self.signal_bindings.get(logical_signal_id)
        if binding is None:
            return None
        return self.point_definitions.get(binding.source_point_key)

    def resolve_output_target(self, logical_output_id: OutputId) -> DevicePointDefinition | None:
        binding = self.output_bindings.get(logical_output_id)
        if binding is None:
            return None
        return self.point_definitions.get(binding.target_point_key)

    def bindings_for_device(self, device_identity_key: str) -> tuple[LogicalSignalBinding, ...]:
        point_keys = set(self.point_keys_for_device(device_identity_key))
        return tuple(binding for binding in self.signal_bindings.values() if binding.source_point_key in point_keys)

    def signal_bindings_for_device_identity(self, device_identity_key: str) -> tuple[tuple[SignalId, LogicalSignalBinding], ...]:
        scoped: list[tuple[SignalId, LogicalSignalBinding]] = []
        for signal_id, binding in self.signal_bindings.items():
            binding_device_identity = self._binding_device_identity(binding.metadata, binding.source_point_key)
            current = self.point_definitions.get(binding.source_point_key)
            if binding_device_identity is not None:
                if binding_device_identity == device_identity_key:
                    scoped.append((signal_id, binding))
                continue
            if (current is not None and current.device_identity_key == device_identity_key) or self._signal_candidates(
                binding=binding,
                device_identity_key=device_identity_key,
            ):
                scoped.append((signal_id, binding))
        return tuple(scoped)

    def output_bindings_for_device_identity(self, device_identity_key: str) -> tuple[tuple[OutputId, LogicalOutputBinding], ...]:
        scoped: list[tuple[OutputId, LogicalOutputBinding]] = []
        for output_id, binding in self.output_bindings.items():
            binding_device_identity = self._binding_device_identity(binding.metadata, binding.target_point_key)
            current = self.point_definitions.get(binding.target_point_key)
            if binding_device_identity is not None:
                if binding_device_identity == device_identity_key:
                    scoped.append((output_id, binding))
                continue
            if (current is not None and current.device_identity_key == device_identity_key) or self._output_candidates(
                binding=binding,
                device_identity_key=device_identity_key,
            ):
                scoped.append((output_id, binding))
        return tuple(scoped)

    def affected_signals_for_point_keys(self, point_keys: tuple[str, ...]) -> tuple[SignalId, ...]:
        keys = set(point_keys)
        return tuple(
            signal_id
            for signal_id, binding in self.signal_bindings.items()
            if binding.source_point_key in keys
        )

    def rebind_signal(self, *, logical_signal_id: SignalId, replacement_point_key: str) -> LogicalSignalBinding:
        current = self.signal_bindings[logical_signal_id]
        rebound = LogicalSignalBinding(
            logical_signal_id=current.logical_signal_id,
            source_point_key=replacement_point_key,
            binding_policy=current.binding_policy,
            metadata=current.metadata,
        )
        self.signal_bindings[logical_signal_id] = rebound
        if self.metrics is not None:
            self.metrics.increment('bindings.signal.rebind.calls')
            self.metrics.set_gauge('bindings.signal.count', len(self.signal_bindings))
        return rebound

    @staticmethod
    def _point_id_from_key(point_key: str) -> str:
        parts = point_key.split(':', 1)
        return point_key if len(parts) == 1 else parts[1]

    def _signal_candidates(self, *, binding: LogicalSignalBinding, device_identity_key: str) -> tuple[DevicePointDefinition, ...]:
        expected_point_id = str(binding.metadata.get('point_id', self._point_id_from_key(binding.source_point_key)))
        return tuple(
            definition
            for definition in self.point_definitions_for_device(device_identity_key)
            if definition.point_ref.point_id == expected_point_id
        )

    def _output_candidates(self, *, binding: LogicalOutputBinding, device_identity_key: str) -> tuple[DevicePointDefinition, ...]:
        expected_point_id = str(binding.metadata.get('point_id', self._point_id_from_key(binding.target_point_key)))
        return tuple(
            definition
            for definition in self.point_definitions_for_device(device_identity_key)
            if definition.point_ref.point_id == expected_point_id
        )

    def build_binding_review(self, *, device_identity_key: str, auto_apply_rebind: bool = True) -> BindingReviewSummary:
        items: list[BindingReviewItem] = []
        resolved_signal_count = 0
        auto_rebound_signal_count = 0
        manual_review_signal_count = 0
        unresolved_signal_count = 0
        blocked_signal_count = 0
        resolved_output_count = 0
        unresolved_output_count = 0

        scoped_signal_bindings = self.signal_bindings_for_device_identity(device_identity_key)
        scoped_output_bindings = self.output_bindings_for_device_identity(device_identity_key)

        for signal_id, binding in scoped_signal_bindings:
            current = self.point_definitions.get(binding.source_point_key)
            if current is not None and current.device_identity_key == device_identity_key and current.enabled:
                resolved_signal_count += 1
                items.append(
                    BindingReviewItem(
                        binding_kind='signal',
                        logical_id=str(signal_id),
                        previous_point_key=binding.source_point_key,
                        resolved_point_key=binding.source_point_key,
                        status=BindingResolutionStatus.RESOLVED,
                        reason='binding resolved against projected point inventory',
                    )
                )
                continue

            candidates = self._signal_candidates(binding=binding, device_identity_key=device_identity_key)
            if len(candidates) == 1:
                replacement = candidates[0]
                if binding.binding_policy in {BindingPolicy.AUTO_REBIND_IF_CONFIDENT, BindingPolicy.SAME_DEVICE_SAME_POINT}:
                    resolved_key = replacement.stable_point_key
                    if auto_apply_rebind and resolved_key != binding.source_point_key:
                        self.rebind_signal(logical_signal_id=signal_id, replacement_point_key=resolved_key)
                    auto_rebound_signal_count += 1
                    items.append(
                        BindingReviewItem(
                            binding_kind='signal',
                            logical_id=str(signal_id),
                            previous_point_key=binding.source_point_key,
                            resolved_point_key=resolved_key,
                            status=BindingResolutionStatus.AUTO_REBOUND,
                            reason='single confident candidate matched by device identity and point id',
                        )
                    )
                    continue
                if binding.binding_policy == BindingPolicy.MANUAL_REVIEW_REQUIRED:
                    manual_review_signal_count += 1
                    items.append(
                        BindingReviewItem(
                            binding_kind='signal',
                            logical_id=str(signal_id),
                            previous_point_key=binding.source_point_key,
                            resolved_point_key=replacement.stable_point_key,
                            status=BindingResolutionStatus.MANUAL_REVIEW_REQUIRED,
                            reason='candidate found but binding policy requires manual confirmation',
                        )
                    )
                    continue
                blocked_signal_count += 1
                items.append(
                    BindingReviewItem(
                        binding_kind='signal',
                        logical_id=str(signal_id),
                        previous_point_key=binding.source_point_key,
                        resolved_point_key=replacement.stable_point_key,
                        status=BindingResolutionStatus.BLOCKED_BY_POLICY,
                        reason='candidate found but strict identity policy blocks rebind',
                    )
                )
                continue

            if len(candidates) > 1:
                manual_review_signal_count += 1
                items.append(
                    BindingReviewItem(
                        binding_kind='signal',
                        logical_id=str(signal_id),
                        previous_point_key=binding.source_point_key,
                        resolved_point_key=None,
                        status=BindingResolutionStatus.MANUAL_REVIEW_REQUIRED,
                        reason='multiple projected points match the prior logical binding target',
                    )
                )
                continue

            unresolved_signal_count += 1
            items.append(
                BindingReviewItem(
                    binding_kind='signal',
                    logical_id=str(signal_id),
                    previous_point_key=binding.source_point_key,
                    resolved_point_key=None,
                    status=BindingResolutionStatus.UNRESOLVED,
                    reason='no projected point matches the prior logical binding target',
                )
            )

        for output_id, binding in scoped_output_bindings:
            current = self.point_definitions.get(binding.target_point_key)
            if current is not None and current.device_identity_key == device_identity_key and current.enabled:
                resolved_output_count += 1
                items.append(
                    BindingReviewItem(
                        binding_kind='output',
                        logical_id=str(output_id),
                        previous_point_key=binding.target_point_key,
                        resolved_point_key=binding.target_point_key,
                        status=BindingResolutionStatus.RESOLVED,
                        reason='output binding resolved against projected point inventory',
                    )
                )
                continue
            candidates = self._output_candidates(binding=binding, device_identity_key=device_identity_key)
            if len(candidates) == 1 and binding.binding_policy in {
                BindingPolicy.AUTO_REBIND_IF_CONFIDENT,
                BindingPolicy.SAME_DEVICE_SAME_POINT,
            }:
                resolved_output_count += 1
                items.append(
                    BindingReviewItem(
                        binding_kind='output',
                        logical_id=str(output_id),
                        previous_point_key=binding.target_point_key,
                        resolved_point_key=candidates[0].stable_point_key,
                        status=BindingResolutionStatus.AUTO_REBOUND,
                        reason='single confident candidate exists for output binding',
                    )
                )
            else:
                unresolved_output_count += 1
                items.append(
                    BindingReviewItem(
                        binding_kind='output',
                        logical_id=str(output_id),
                        previous_point_key=binding.target_point_key,
                        resolved_point_key=None if len(candidates) != 1 else candidates[0].stable_point_key,
                        status=BindingResolutionStatus.MANUAL_REVIEW_REQUIRED if len(candidates) > 1 else BindingResolutionStatus.UNRESOLVED,
                        reason='output binding requires review against current projected point inventory',
                    )
                )

        if self.metrics is not None:
            self.metrics.increment('bindings.review.calls')
            self.metrics.set_gauge('bindings.review.manual_signal.count', manual_review_signal_count)
            self.metrics.set_gauge('bindings.review.unresolved_signal.count', unresolved_signal_count)
            self.metrics.set_gauge('bindings.review.scope.signal.count', len(scoped_signal_bindings))
            self.metrics.set_gauge('bindings.review.scope.output.count', len(scoped_output_bindings))

        return BindingReviewSummary(
            total_signal_binding_count=len(scoped_signal_bindings),
            total_output_binding_count=len(scoped_output_bindings),
            resolved_signal_count=resolved_signal_count,
            auto_rebound_signal_count=auto_rebound_signal_count,
            manual_review_signal_count=manual_review_signal_count,
            unresolved_signal_count=unresolved_signal_count,
            blocked_signal_count=blocked_signal_count,
            resolved_output_count=resolved_output_count,
            unresolved_output_count=unresolved_output_count,
            items=tuple(items),
        )
