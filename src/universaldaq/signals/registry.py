from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping

from universaldaq.common import EventTime, RuntimeMetricsStore, SignalId, SignalQuality

from .models import DerivedSignalDefinition, SignalDefinition


@dataclass(frozen=True, slots=True, kw_only=True)
class SignalSnapshot:
    signal_id: SignalId
    value: str
    quality: SignalQuality
    timestamp: EventTime


@dataclass(frozen=True, slots=True, kw_only=True)
class DerivedEvaluationResult:
    snapshot: SignalSnapshot
    dependency_values: Mapping[str, str]


@dataclass(slots=True)
class SignalRegistry:
    definitions: dict[SignalId, SignalDefinition] = field(default_factory=dict)
    derived_definitions: dict[SignalId, DerivedSignalDefinition] = field(default_factory=dict)
    snapshots: dict[SignalId, SignalSnapshot] = field(default_factory=dict)
    metrics: RuntimeMetricsStore | None = None

    def register_signal(self, definition: SignalDefinition) -> None:
        self.definitions[definition.signal_id] = definition
        if self.metrics is not None:
            self.metrics.increment('signals.definition.register.calls')
            self.metrics.set_gauge('signals.definition.count', len(self.definitions))

    def register_derived_signal(self, definition: DerivedSignalDefinition) -> None:
        self.derived_definitions[definition.signal_id] = definition
        self.definitions[definition.signal_id] = SignalDefinition(
            signal_id=definition.signal_id,
            display_name=definition.display_name,
            engineering_units=definition.engineering_units,
            quality=definition.quality,
        )
        if self.metrics is not None:
            self.metrics.increment('signals.derived_definition.register.calls')
            self.metrics.set_gauge('signals.derived_definition.count', len(self.derived_definitions))
            self.metrics.set_gauge('signals.definition.count', len(self.definitions))

    def rename_signal(self, signal_id: SignalId, new_display_name: str) -> SignalDefinition:
        definition = self.definitions[signal_id]
        renamed = definition.renamed(new_display_name)
        self.definitions[signal_id] = renamed
        if signal_id in self.derived_definitions:
            self.derived_definitions[signal_id] = replace(self.derived_definitions[signal_id], display_name=new_display_name)
        if self.metrics is not None:
            self.metrics.increment('signals.rename.calls')
        return renamed

    def publish_snapshot(self, snapshot: SignalSnapshot) -> None:
        self.snapshots[snapshot.signal_id] = snapshot
        if self.metrics is not None:
            self.metrics.increment('signals.snapshot.publish.calls')
            self.metrics.set_gauge('signals.snapshot.count', len(self.snapshots))

    def evaluate_derived(self, signal_id: SignalId, *, value: str, timestamp: EventTime) -> DerivedEvaluationResult:
        definition = self.derived_definitions[signal_id]
        dependency_values = {
            str(dep): self.snapshots[dep].value
            for dep in definition.dependencies
            if dep in self.snapshots
        }
        quality = SignalQuality.GOOD if len(dependency_values) == len(definition.dependencies) else SignalQuality.STALE
        snapshot = SignalSnapshot(signal_id=signal_id, value=value, quality=quality, timestamp=timestamp)
        self.publish_snapshot(snapshot)
        if self.metrics is not None:
            self.metrics.increment('signals.derived.evaluate.calls')
        return DerivedEvaluationResult(snapshot=snapshot, dependency_values=dependency_values)
