from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Mapping

from universaldaq.adapters import AdapterCapability, AdapterManagerService, AdapterPollResult, PointClass
from universaldaq.common import EventTime, RuntimeMetricsStore

from .models import (
    CanonicalTagDefinition,
    CanonicalTagProjection,
    CanonicalTagSample,
    MultiAdapterPollBatch,
    TagDirection,
    TagTimestampSource,
    TagValueType,
)

_POINT_CLASS_TO_VALUE_TYPE = {
    PointClass.ANALOG: TagValueType.ANALOG,
    PointClass.DIGITAL: TagValueType.DIGITAL,
    PointClass.STATUS: TagValueType.STATUS,
    PointClass.COMMAND: TagValueType.COMMAND,
}


def _slug(value: str) -> str:
    pieces: list[str] = []
    current = []
    for ch in value:
        if ch.isalnum():
            current.append(ch.lower())
        else:
            if current:
                pieces.append(''.join(current))
                current = []
    if current:
        pieces.append(''.join(current))
    return '_'.join(piece for piece in pieces if piece) or 'tag'


@dataclass(slots=True)
class CanonicalTagRegistryService:
    definitions: dict[str, CanonicalTagDefinition] = field(default_factory=dict)
    latest_samples: dict[str, CanonicalTagSample] = field(default_factory=dict)
    metrics: RuntimeMetricsStore | None = None

    def register_capability(self, capability: AdapterCapability) -> tuple[CanonicalTagDefinition, ...]:
        projected: list[CanonicalTagDefinition] = []
        for point in capability.readable_points:
            definition = self._definition_from_point(
                capability=capability,
                point_id=point.point_id,
                display_name=point.display_name or point.point_id,
                units=point.units,
                point_class=point.point_class,
                writable=False,
                metadata=point.metadata,
            )
            self.definitions[definition.tag_key] = definition
            projected.append(definition)
        for point in capability.writable_points:
            definition = self._definition_from_point(
                capability=capability,
                point_id=point.point_id,
                display_name=point.display_name or point.point_id,
                units=point.units,
                point_class=point.point_class,
                writable=True,
                metadata=point.metadata,
            )
            self.definitions[definition.tag_key] = definition
            projected.append(definition)
        if self.metrics is not None:
            self.metrics.increment('tags.definition.register.calls')
            self.metrics.set_gauge('tags.definition.count', len(self.definitions))
        return tuple(projected)

    def project_poll_result(self, poll_result: AdapterPollResult) -> CanonicalTagProjection:
        definitions: list[CanonicalTagDefinition] = []
        samples: list[CanonicalTagSample] = []
        for snapshot in poll_result.snapshots:
            tag_key = self._tag_key(adapter_id=snapshot.point.adapter_id, point_id=snapshot.point.point_id)
            definition = self.definitions.get(tag_key)
            if definition is None:
                definition = CanonicalTagDefinition(
                    tag_key=tag_key,
                    canonical_name=self._canonical_name(snapshot.point.adapter_id, snapshot.point.point_id),
                    display_name=snapshot.point.display_name or snapshot.point.point_id,
                    adapter_id=snapshot.point.adapter_id,
                    device_instance=_slug(snapshot.point.adapter_id),
                    source_point_id=snapshot.point.point_id,
                    direction=TagDirection.INPUT,
                    value_type=_POINT_CLASS_TO_VALUE_TYPE.get(snapshot.point.point_class, TagValueType.UNKNOWN),
                    engineering_units=snapshot.point.units,
                    writable=False,
                    historize=True,
                    alarmable=snapshot.point.point_class in {PointClass.ANALOG, PointClass.DIGITAL, PointClass.STATUS},
                    metadata=dict(snapshot.point.metadata),
                )
                self.definitions[tag_key] = definition
            definitions.append(definition)
            sample = CanonicalTagSample(
                tag_key=definition.tag_key,
                value=snapshot.engineering_value,
                quality=snapshot.quality,
                sample_timestamp=snapshot.source_timestamp,
                timestamp_source=TagTimestampSource.SOURCE,
                source_timestamp=snapshot.source_timestamp,
                received_timestamp=snapshot.received_timestamp,
                metadata={
                    'adapter_id': snapshot.point.adapter_id,
                    'point_id': snapshot.point.point_id,
                    **{key: str(value) for key, value in snapshot.metadata.items()},
                },
            )
            self.latest_samples[definition.tag_key] = sample
            samples.append(sample)
        if self.metrics is not None:
            self.metrics.increment('tags.sample.project.calls')
            self.metrics.increment('tags.sample.projected.count', len(samples))
            self.metrics.set_gauge('tags.sample.latest.count', len(self.latest_samples))
        return CanonicalTagProjection(definitions=tuple(definitions), samples=tuple(samples))

    def latest_sample_rows(self) -> tuple[dict[str, object], ...]:
        rows: list[dict[str, object]] = []
        for definition in sorted(self.definitions.values(), key=lambda row: row.tag_key):
            sample = self.latest_samples.get(definition.tag_key)
            if sample is None:
                continue
            rows.append(
                {
                    'tag_key': definition.tag_key,
                    'canonical_name': definition.canonical_name,
                    'display_name': definition.display_name,
                    'adapter_id': definition.adapter_id,
                    'device_instance': definition.device_instance,
                    'source_point_id': definition.source_point_id,
                    'value_type': definition.value_type.value,
                    'value': sample.value,
                    'quality': sample.quality.value,
                    'sample_timestamp': int(sample.sample_timestamp),
                    'units': '' if definition.engineering_units is None else definition.engineering_units,
                }
            )
        return tuple(rows)

    def counts_by_adapter(self) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for definition in self.definitions.values():
            if definition.tag_key in self.latest_samples:
                counts[definition.adapter_id] += 1
        return dict(sorted(counts.items()))

    def _definition_from_point(
        self,
        *,
        capability: AdapterCapability,
        point_id: str,
        display_name: str,
        units: str | None,
        point_class: PointClass,
        writable: bool,
        metadata: Mapping[str, str],
    ) -> CanonicalTagDefinition:
        tag_key = self._tag_key(adapter_id=capability.adapter_id, point_id=point_id)
        return CanonicalTagDefinition(
            tag_key=tag_key,
            canonical_name=self._canonical_name(capability.adapter_id, point_id),
            display_name=display_name,
            adapter_id=capability.adapter_id,
            device_instance=_slug(capability.adapter_id),
            source_point_id=point_id,
            direction=TagDirection.OUTPUT if writable else TagDirection.INPUT,
            value_type=_POINT_CLASS_TO_VALUE_TYPE.get(point_class, TagValueType.UNKNOWN),
            engineering_units=units,
            writable=writable,
            historize=not writable,
            alarmable=point_class in {PointClass.ANALOG, PointClass.DIGITAL, PointClass.STATUS},
            metadata={
                **{key: str(value) for key, value in capability.metadata.items()},
                **{key: str(value) for key, value in metadata.items()},
            },
        )

    @staticmethod
    def _tag_key(*, adapter_id: str, point_id: str) -> str:
        return f'{adapter_id}:{point_id}'

    @staticmethod
    def _canonical_name(adapter_id: str, point_id: str) -> str:
        return f'{_slug(adapter_id)}.{_slug(point_id)}'


@dataclass(slots=True)
class MultiAdapterAcquisitionBroker:
    adapter_manager: AdapterManagerService
    tag_registry: CanonicalTagRegistryService
    metrics: RuntimeMetricsStore | None = None

    def poll(self, *, adapter_ids: tuple[str, ...], timestamp: EventTime) -> MultiAdapterPollBatch:
        definitions: list[CanonicalTagDefinition] = []
        samples: list[CanonicalTagSample] = []
        diagnostics: list[dict[str, object]] = []
        active_adapter_ids: list[str] = []
        for adapter_id in adapter_ids:
            adapter = self.adapter_manager.adapters.get(adapter_id)
            if adapter is None:
                continue
            active_adapter_ids.append(adapter_id)
            definitions.extend(self.tag_registry.register_capability(adapter.capability()))
            poll_result = self.adapter_manager.poll_adapter(adapter_id=adapter_id, timestamp=timestamp)
            if poll_result is None:
                continue
            projection = self.tag_registry.project_poll_result(poll_result)
            samples.extend(projection.samples)
            diagnostics.append(
                {
                    'adapter_id': adapter_id,
                    'snapshot_count': len(poll_result.snapshots),
                    'diagnostic_rows': len(poll_result.diagnostics),
                }
            )
        if self.metrics is not None:
            self.metrics.increment('tags.broker.poll.calls')
            self.metrics.increment('tags.broker.poll.adapters', len(active_adapter_ids))
            self.metrics.increment('tags.broker.poll.samples', len(samples))
        return MultiAdapterPollBatch(
            polled_at=timestamp,
            adapter_ids=tuple(active_adapter_ids),
            definitions=tuple(definitions),
            samples=tuple(samples),
            diagnostics=tuple(diagnostics),
        )
