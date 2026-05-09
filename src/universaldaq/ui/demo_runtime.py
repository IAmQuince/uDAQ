from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import math
from typing import Deque

from .demo_shell import DEFAULT_DEMO_SCENARIOS, UserDemoScenario


_MAX_HISTORY = 720


@dataclass(frozen=True, slots=True, kw_only=True)
class DemoSignalDescriptor:
    signal_id: str
    units: str
    source_class: str
    plottable: bool = True
    write_safe: bool = False
    labels_by_lens: dict[str, str] = field(default_factory=dict)

    def label_for_lens(self, lens_id: str) -> str:
        return self.labels_by_lens.get(lens_id, self.labels_by_lens.get('logical', self.signal_id))


@dataclass(frozen=True, slots=True, kw_only=True)
class DemoSignalSnapshot:
    descriptor: DemoSignalDescriptor
    value: float
    quality_label: str
    freshness_label: str
    alarm_severity: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DemoTraceSeries:
    signal_id: str
    x_values: tuple[float, ...]
    y_values: tuple[float, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class DemoScenarioSnapshot:
    scenario: UserDemoScenario
    elapsed_seconds: float
    signal_snapshots: tuple[DemoSignalSnapshot, ...]
    event_log: tuple[str, ...]


class DemoRuntimeEngine:
    def __init__(self, *, scenario_id: str = 'trace_styling_demo') -> None:
        self._elapsed_seconds = 0.0
        self._histories: dict[str, Deque[tuple[float, float]]] = {}
        self._event_log: Deque[str] = deque(maxlen=50)
        self._active_scenario = self._resolve_scenario(scenario_id)
        self._descriptors = self._build_descriptors()
        self._latest_values: dict[str, float] = {descriptor.signal_id: 0.0 for descriptor in self._descriptors}
        self._quality_labels: dict[str, str] = {descriptor.signal_id: 'simulated' for descriptor in self._descriptors}
        self._freshness_labels: dict[str, str] = {descriptor.signal_id: 'simulated' for descriptor in self._descriptors}
        self._alarm_severities: dict[str, str] = {descriptor.signal_id: 'normal' for descriptor in self._descriptors}
        for descriptor in self._descriptors:
            self._histories[descriptor.signal_id] = deque(maxlen=_MAX_HISTORY)
        self._event_log.append(f'loaded scenario: {self._active_scenario.display_name}')

    @property
    def active_scenario(self) -> UserDemoScenario:
        return self._active_scenario

    @property
    def active_scenario_id(self) -> str:
        return self._active_scenario.scenario_id

    @staticmethod
    def available_scenarios() -> tuple[UserDemoScenario, ...]:
        return DEFAULT_DEMO_SCENARIOS

    def _resolve_scenario(self, scenario_id: str) -> UserDemoScenario:
        for scenario in DEFAULT_DEMO_SCENARIOS:
            if scenario.scenario_id == scenario_id:
                return scenario
        return DEFAULT_DEMO_SCENARIOS[0]

    def activate_scenario(self, scenario_id: str) -> None:
        self._active_scenario = self._resolve_scenario(scenario_id)
        self._elapsed_seconds = 0.0
        self._descriptors = self._build_descriptors()
        self._latest_values = {descriptor.signal_id: 0.0 for descriptor in self._descriptors}
        self._quality_labels = {descriptor.signal_id: 'simulated' for descriptor in self._descriptors}
        self._freshness_labels = {descriptor.signal_id: 'simulated' for descriptor in self._descriptors}
        self._alarm_severities = {descriptor.signal_id: 'normal' for descriptor in self._descriptors}
        self._histories = {descriptor.signal_id: deque(maxlen=_MAX_HISTORY) for descriptor in self._descriptors}
        self._event_log.clear()
        self._event_log.append(f'loaded scenario: {self._active_scenario.display_name}')

    def _build_descriptors(self) -> tuple[DemoSignalDescriptor, ...]:
        base = (
            DemoSignalDescriptor(
                signal_id='sig_demo_wave_0',
                units='V',
                source_class='raw',
                labels_by_lens={
                    'hardware': 'RPI_01.GPIO17',
                    'raw': 'garage_button_raw',
                    'logical': 'garage_button_raw',
                    'derived': 'garage_button_debounced',
                    'control': 'garage_button_command_gate',
                    'saved': 'Startup Demo / Button',
                },
            ),
            DemoSignalDescriptor(
                signal_id='sig_demo_temp_0',
                units='C',
                source_class='logical',
                labels_by_lens={
                    'hardware': 'EDGE_01.ANALOG_TEMP0',
                    'raw': 'garage_temp_raw',
                    'logical': 'garage_temp_filtered',
                    'derived': 'garage_temp_rate',
                    'control': 'garage_temp_watch',
                    'saved': 'Thermal / Garage Temp',
                },
            ),
            DemoSignalDescriptor(
                signal_id='sig_demo_pressure_0',
                units='bar',
                source_class='derived',
                labels_by_lens={
                    'hardware': 'EDGE_01.ANALOG_0',
                    'raw': 'cell_pressure_raw',
                    'logical': 'cell_pressure_filtered',
                    'derived': 'cell_pressure_rate',
                    'control': 'purge_threshold_watch',
                    'saved': 'Cell Loop / Pressure',
                },
            ),
            DemoSignalDescriptor(
                signal_id='sig_demo_flow_0',
                units='slpm',
                source_class='derived',
                labels_by_lens={
                    'hardware': 'EDGE_01.ANALOG_1',
                    'raw': 'loop_flow_raw',
                    'logical': 'loop_flow_filtered',
                    'derived': 'loop_flow_margin',
                    'control': 'flow_guard_signal',
                    'saved': 'Cell Loop / Flow',
                },
            ),
            DemoSignalDescriptor(
                signal_id='sig_demo_dac_cmd',
                units='V',
                source_class='control',
                write_safe=True,
                labels_by_lens={
                    'hardware': 'EDGE_01.ANALOG_OUT_0',
                    'raw': 'fan_voltage_cmd_raw',
                    'logical': 'fan_voltage_cmd',
                    'derived': 'fan_voltage_cmd_filtered',
                    'control': 'fan_voltage_cmd',
                    'saved': 'Outputs / Fan DAC',
                },
            ),
            DemoSignalDescriptor(
                signal_id='sig_demo_alarm_bus',
                units='score',
                source_class='derived',
                labels_by_lens={
                    'hardware': 'virtual.alarm.bus',
                    'raw': 'alarm_bus_raw',
                    'logical': 'alarm_bus',
                    'derived': 'alarm_severity_score',
                    'control': 'alarm_watch',
                    'saved': 'Alarm Watch',
                },
            ),
        )
        if self._active_scenario.scenario_id == 'trace_styling_demo':
            return base[:4]
        if self._active_scenario.scenario_id == 'alarm_visualization_demo':
            return base[1:6]
        if self._active_scenario.scenario_id == 'signal_lineage_demo':
            return base[:5]
        return base

    def step(self, *, dt_seconds: float = 0.15) -> DemoScenarioSnapshot:
        self._elapsed_seconds += dt_seconds
        t = self._elapsed_seconds
        for index, descriptor in enumerate(self._descriptors):
            phase = t + index * 0.75
            if descriptor.signal_id == 'sig_demo_wave_0':
                value = 2.0 if math.sin(phase) > 0.45 else 0.0
            elif descriptor.signal_id == 'sig_demo_temp_0':
                value = 22.0 + 2.4 * math.sin(phase / 3.0) + 0.35 * math.cos(phase / 1.8)
            elif descriptor.signal_id == 'sig_demo_pressure_0':
                value = 1.7 + 0.65 * math.sin(phase / 1.7)
            elif descriptor.signal_id == 'sig_demo_flow_0':
                value = 5.5 + 1.4 * math.cos(phase / 2.1)
            elif descriptor.signal_id == 'sig_demo_dac_cmd':
                temp = self._latest_values.get('sig_demo_temp_0', 22.0)
                flow = self._latest_values.get('sig_demo_flow_0', 5.5)
                value = max(0.0, min(5.0, 0.45 * (temp - 20.0) + 0.2 * (flow - 4.0)))
            elif descriptor.signal_id == 'sig_demo_alarm_bus':
                pressure = self._latest_values.get('sig_demo_pressure_0', 1.7)
                temp = self._latest_values.get('sig_demo_temp_0', 22.0)
                value = max(0.0, pressure * 10.0 + max(0.0, temp - 23.5) * 3.0)
            else:
                value = math.sin(phase)
            self._latest_values[descriptor.signal_id] = value
            self._histories[descriptor.signal_id].append((t, value))
            severity = self._derive_alarm_severity(signal_id=descriptor.signal_id, value=value)
            previous = self._alarm_severities.get(descriptor.signal_id, 'normal')
            self._alarm_severities[descriptor.signal_id] = severity
            if severity != previous and severity != 'normal':
                self._event_log.append(f'{descriptor.label_for_lens("logical")}: {severity}')
        return self.snapshot()

    def _derive_alarm_severity(self, *, signal_id: str, value: float) -> str:
        if signal_id == 'sig_demo_pressure_0':
            if value > 2.25:
                return 'critical'
            if value > 2.0:
                return 'high'
            if value > 1.85:
                return 'warning'
            return 'normal'
        if signal_id == 'sig_demo_temp_0':
            if value > 24.4:
                return 'warning'
            return 'normal'
        if signal_id == 'sig_demo_alarm_bus':
            if value > 26.0:
                return 'critical'
            if value > 22.0:
                return 'high'
            if value > 18.0:
                return 'warning'
            return 'normal'
        if signal_id == 'sig_demo_dac_cmd' and value > 4.0:
            return 'warning'
        return 'normal'

    def signal_descriptors(self, *, lens_id: str | None = None) -> tuple[DemoSignalDescriptor, ...]:
        _ = lens_id
        return self._descriptors

    def signal_snapshots(self, *, lens_id: str | None = None) -> tuple[DemoSignalSnapshot, ...]:
        _ = lens_id
        return tuple(
            DemoSignalSnapshot(
                descriptor=descriptor,
                value=self._latest_values[descriptor.signal_id],
                quality_label=self._quality_labels[descriptor.signal_id],
                freshness_label=self._freshness_labels[descriptor.signal_id],
                alarm_severity=self._alarm_severities[descriptor.signal_id],
            )
            for descriptor in self._descriptors
        )

    def trace_series(self, signal_id: str) -> DemoTraceSeries:
        history = tuple(self._histories.get(signal_id, ()))
        return DemoTraceSeries(
            signal_id=signal_id,
            x_values=tuple(item[0] for item in history),
            y_values=tuple(item[1] for item in history),
        )

    def snapshot(self) -> DemoScenarioSnapshot:
        return DemoScenarioSnapshot(
            scenario=self._active_scenario,
            elapsed_seconds=self._elapsed_seconds,
            signal_snapshots=self.signal_snapshots(),
            event_log=tuple(self._event_log),
        )
