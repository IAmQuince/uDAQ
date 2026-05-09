from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import Mapping

from universaldaq.common import EventTime, RuntimeMetricsStore

from .models import DeviceIdentity


class MatchConfidence(StrEnum):
    EXACT_MATCH = 'exact_match'
    PROBABLE_MATCH = 'probable_match'
    POSSIBLE_MATCH = 'possible_match'
    NO_MATCH = 'no_match'


class ConnectionState(StrEnum):
    ATTACHED = 'attached'
    DISCONNECTED = 'disconnected'


class ReconciliationOutcomeKind(StrEnum):
    NEW_DEVICE_ENROLLED = 'new_device_enrolled'
    RESTORED_EXACT = 'restored_exact'
    RESTORED_WITH_PORT_CHANGE = 'restored_with_port_change'
    RESTORED_PARTIAL = 'restored_partial'
    CANDIDATE_REMAP_REQUIRES_REVIEW = 'candidate_remap_requires_review'
    REPLACEMENT_DETECTED = 'replacement_detected'


@dataclass(frozen=True, slots=True, kw_only=True)
class DeviceRecord:
    device_record_id: str
    stable_identity_key: str
    display_name: str
    serial_number: str | None = None
    vendor: str | None = None
    model: str | None = None
    last_transport_path: str | None = None
    current_connection_instance_id: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class ConnectionInstance:
    connection_instance_id: str
    device_record_id: str
    provider_id: str
    transport_path: str | None
    connected_at: EventTime
    state: ConnectionState = ConnectionState.ATTACHED
    disconnected_at: EventTime | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class RemapCandidate:
    device_record_id: str
    display_name: str
    confidence: MatchConfidence
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ReconciliationOutcome:
    kind: ReconciliationOutcomeKind
    confidence: MatchConfidence
    device_record: DeviceRecord
    connection: ConnectionInstance
    remap_candidates: tuple[RemapCandidate, ...] = field(default_factory=tuple)
    reason: str | None = None


@dataclass(slots=True)
class DeviceRegistryService:
    device_records: dict[str, DeviceRecord] = field(default_factory=dict)
    connections: dict[str, ConnectionInstance] = field(default_factory=dict)
    metrics: RuntimeMetricsStore | None = None

    def _record_id(self, identity: DeviceIdentity) -> str:
        stable_key = identity.stable_key or identity.summary
        return f'device::{stable_key}'

    def _connection_id(self, *, record_id: str, timestamp: EventTime) -> str:
        return f'conn::{record_id}::{int(timestamp)}::{len(self.connections) + 1}'

    def _identity_family_matches(self, identity: DeviceIdentity, record: DeviceRecord) -> bool:
        return bool(identity.vendor == record.vendor and identity.model == record.model)

    def register_or_attach(
        self,
        *,
        identity: DeviceIdentity,
        provider_id: str,
        transport_path: str | None,
        timestamp: EventTime,
    ) -> ReconciliationOutcome:
        if self.metrics is not None:
            self.metrics.increment('device_registry.register_or_attach.calls')
            with self.metrics.measure('device_registry.register_or_attach.ms'):
                outcome = self._register_or_attach_impl(
                    identity=identity,
                    provider_id=provider_id,
                    transport_path=transport_path,
                    timestamp=timestamp,
                )
            self.metrics.set_gauge('device_registry.records.count', len(self.device_records))
            self.metrics.set_gauge('device_registry.connections.count', len(self.connections))
            return outcome
        return self._register_or_attach_impl(
            identity=identity,
            provider_id=provider_id,
            transport_path=transport_path,
            timestamp=timestamp,
        )

    def _register_or_attach_impl(
        self,
        *,
        identity: DeviceIdentity,
        provider_id: str,
        transport_path: str | None,
        timestamp: EventTime,
    ) -> ReconciliationOutcome:
        stable_record = self.device_records.get(self._record_id(identity))
        if stable_record is not None:
            return self._reattach_existing(
                record=stable_record,
                provider_id=provider_id,
                transport_path=transport_path,
                timestamp=timestamp,
            )

        family_matches = [record for record in self.device_records.values() if self._identity_family_matches(identity, record)]
        if identity.serial_number is None and family_matches:
            provisional = self._create_device_record(identity=identity, transport_path=transport_path)
            connection = self._attach_connection(record=provisional, provider_id=provider_id, transport_path=transport_path, timestamp=timestamp)
            candidates = tuple(
                RemapCandidate(
                    device_record_id=record.device_record_id,
                    display_name=record.display_name,
                    confidence=MatchConfidence.POSSIBLE_MATCH,
                    reason='same vendor/model family without stable serial identity',
                )
                for record in family_matches
            )
            if self.metrics is not None:
                self.metrics.increment('device_registry.reconciliation.ambiguous.calls')
                self.metrics.set_gauge('device_registry.reconciliation.remap_candidates.count', len(candidates))
            return ReconciliationOutcome(
                kind=ReconciliationOutcomeKind.CANDIDATE_REMAP_REQUIRES_REVIEW,
                confidence=MatchConfidence.POSSIBLE_MATCH,
                device_record=provisional,
                connection=connection,
                remap_candidates=candidates,
                reason='device family matches existing records but stable identity is incomplete',
            )

        new_record = self._create_device_record(identity=identity, transport_path=transport_path)
        connection = self._attach_connection(record=new_record, provider_id=provider_id, transport_path=transport_path, timestamp=timestamp)
        if self.metrics is not None:
            self.metrics.increment('device_registry.reconciliation.new_device.calls')
        return ReconciliationOutcome(
            kind=ReconciliationOutcomeKind.NEW_DEVICE_ENROLLED,
            confidence=MatchConfidence.NO_MATCH,
            device_record=new_record,
            connection=connection,
            reason='no existing stable identity matched',
        )

    def _create_device_record(self, *, identity: DeviceIdentity, transport_path: str | None) -> DeviceRecord:
        record = DeviceRecord(
            device_record_id=self._record_id(identity),
            stable_identity_key=identity.stable_key,
            display_name=identity.display_name,
            serial_number=identity.serial_number,
            vendor=identity.vendor,
            model=identity.model,
            last_transport_path=transport_path,
            metadata={
                'transport': '' if identity.transport is None else identity.transport,
                'firmware_version': '' if identity.firmware_version is None else identity.firmware_version,
            },
        )
        self.device_records[record.device_record_id] = record
        return record

    def _attach_connection(
        self,
        *,
        record: DeviceRecord,
        provider_id: str,
        transport_path: str | None,
        timestamp: EventTime,
    ) -> ConnectionInstance:
        connection = ConnectionInstance(
            connection_instance_id=self._connection_id(record_id=record.device_record_id, timestamp=timestamp),
            device_record_id=record.device_record_id,
            provider_id=provider_id,
            transport_path=transport_path,
            connected_at=timestamp,
            state=ConnectionState.ATTACHED,
        )
        self.connections[connection.connection_instance_id] = connection
        self.device_records[record.device_record_id] = replace(
            record,
            current_connection_instance_id=connection.connection_instance_id,
            last_transport_path=transport_path,
        )
        return connection

    def _reattach_existing(
        self,
        *,
        record: DeviceRecord,
        provider_id: str,
        transport_path: str | None,
        timestamp: EventTime,
    ) -> ReconciliationOutcome:
        previous_path = record.last_transport_path
        connection = self._attach_connection(record=record, provider_id=provider_id, transport_path=transport_path, timestamp=timestamp)
        kind = ReconciliationOutcomeKind.RESTORED_EXACT
        reason = 'stable identity matched an existing device record'
        if previous_path is not None and transport_path is not None and previous_path != transport_path:
            kind = ReconciliationOutcomeKind.RESTORED_WITH_PORT_CHANGE
            reason = 'stable identity matched and the device returned on a different transport path'
            if self.metrics is not None:
                self.metrics.increment('device_registry.reconciliation.port_change.calls')
        else:
            if self.metrics is not None:
                self.metrics.increment('device_registry.reconciliation.exact.calls')
        return ReconciliationOutcome(
            kind=kind,
            confidence=MatchConfidence.EXACT_MATCH,
            device_record=self.device_records[record.device_record_id],
            connection=connection,
            reason=reason,
        )

    def disconnect(self, *, connection_instance_id: str, timestamp: EventTime) -> ConnectionInstance:
        if self.metrics is not None:
            self.metrics.increment('device_registry.disconnect.calls')
            with self.metrics.measure('device_registry.disconnect.ms'):
                disconnected = self._disconnect_impl(connection_instance_id=connection_instance_id, timestamp=timestamp)
            self.metrics.set_gauge('device_registry.connections.count', len(self.connections))
            return disconnected
        return self._disconnect_impl(connection_instance_id=connection_instance_id, timestamp=timestamp)

    def _disconnect_impl(self, *, connection_instance_id: str, timestamp: EventTime) -> ConnectionInstance:
        connection = self.connections[connection_instance_id]
        disconnected = replace(connection, state=ConnectionState.DISCONNECTED, disconnected_at=timestamp)
        self.connections[connection_instance_id] = disconnected
        record = self.device_records[connection.device_record_id]
        if record.current_connection_instance_id == connection_instance_id:
            self.device_records[record.device_record_id] = replace(record, current_connection_instance_id=None)
        return disconnected

    def active_records(self) -> tuple[DeviceRecord, ...]:
        return tuple(record for record in self.device_records.values() if record.current_connection_instance_id is not None)

    def records_for_family(self, *, vendor: str | None, model: str | None) -> tuple[DeviceRecord, ...]:
        return tuple(
            record
            for record in self.device_records.values()
            if record.vendor == vendor and record.model == model
        )
