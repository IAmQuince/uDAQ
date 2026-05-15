from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping

from universaldaq.common import EventTime, SignalQuality


class TagDirection(StrEnum):
    INPUT = 'input'
    OUTPUT = 'output'
    DERIVED = 'derived'
    VIRTUAL = 'virtual'


class TagValueType(StrEnum):
    ANALOG = 'analog'
    DIGITAL = 'digital'
    STATUS = 'status'
    COMMAND = 'command'
    TEXT = 'text'
    UNKNOWN = 'unknown'


class TagTimestampSource(StrEnum):
    SOURCE = 'source'
    RECEIVED = 'received'
    SYNTHESIZED = 'synthesized'


@dataclass(frozen=True, slots=True, kw_only=True)
class CanonicalTagDefinition:
    tag_key: str
    canonical_name: str
    display_name: str
    adapter_id: str
    device_instance: str
    source_point_id: str
    direction: TagDirection
    value_type: TagValueType
    engineering_units: str | None = None
    writable: bool = False
    historize: bool = True
    alarmable: bool = True
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class CanonicalTagSample:
    tag_key: str
    value: str
    quality: SignalQuality
    sample_timestamp: EventTime
    timestamp_source: TagTimestampSource
    source_timestamp: EventTime
    received_timestamp: EventTime
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class CanonicalTagProjection:
    definitions: tuple[CanonicalTagDefinition, ...]
    samples: tuple[CanonicalTagSample, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class MultiAdapterPollBatch:
    polled_at: EventTime
    adapter_ids: tuple[str, ...]
    definitions: tuple[CanonicalTagDefinition, ...]
    samples: tuple[CanonicalTagSample, ...]
    diagnostics: tuple[dict[str, object], ...] = field(default_factory=tuple)
