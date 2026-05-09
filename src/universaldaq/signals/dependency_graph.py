from __future__ import annotations

from collections import defaultdict

from universaldaq.common import SignalId, ValidationFinding, ValidationReport
from .models import DerivedSignalDefinition


def dependency_graph(definitions: tuple[DerivedSignalDefinition, ...]) -> dict[SignalId, tuple[SignalId, ...]]:
    return {definition.signal_id: definition.dependencies for definition in definitions}


def find_cycles(definitions: tuple[DerivedSignalDefinition, ...]) -> tuple[tuple[SignalId, ...], ...]:
    graph = dependency_graph(definitions)
    states: dict[SignalId, int] = defaultdict(int)
    stack: list[SignalId] = []
    cycles: list[tuple[SignalId, ...]] = []

    def visit(node: SignalId) -> None:
        state = states[node]
        if state == 1:
            if node in stack:
                start = stack.index(node)
                cycles.append(tuple(stack[start:] + [node]))
            return
        if state == 2:
            return
        states[node] = 1
        stack.append(node)
        for child in graph.get(node, ()):  # missing leaves are allowed here
            if child in graph:
                visit(child)
        stack.pop()
        states[node] = 2

    for node in graph:
        visit(node)
    return tuple(cycles)


def validate_derived_signals(definitions: tuple[DerivedSignalDefinition, ...]) -> ValidationReport:
    findings: list[ValidationFinding] = []
    cycles = find_cycles(definitions)
    for cycle in cycles:
        names = " -> ".join(str(item) for item in cycle)
        findings.append(ValidationFinding(code="derived_cycle", message=f"cycle detected: {names}"))
    return ValidationReport(findings=tuple(findings))
