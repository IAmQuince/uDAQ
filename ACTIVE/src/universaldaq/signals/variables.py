from __future__ import annotations

import ast
from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping

from universaldaq.common import EventTime, RuntimeMetricsStore, SignalId, SignalQuality, VariableId

from .registry import SignalRegistry

MAX_VARIABLE_EXPRESSION_LENGTH = 256
MAX_VARIABLE_EXPRESSION_NODES = 64
MAX_VARIABLE_EVALUATION_STEPS = 128
MAX_VARIABLE_POWER_ABS_EXPONENT = 8


class VariableSourceKind(StrEnum):
    SIGNAL = 'signal'
    CONSTANT = 'constant'
    EXPRESSION = 'expression'
    VARIABLE = 'variable'


class VariableState(StrEnum):
    UNRESOLVED = 'unresolved'
    HEALTHY = 'healthy'
    DEGRADED = 'degraded'
    STALE = 'stale'
    INVALID = 'invalid'
    SUBSTITUTED = 'substituted'
    INHIBITED = 'inhibited'


@dataclass(frozen=True, slots=True, kw_only=True)
class VariableDefinition:
    variable_id: VariableId
    display_name: str
    engineering_units: str | None = None
    source_kind: VariableSourceKind = VariableSourceKind.EXPRESSION
    expression: str | None = None
    constant_value: str | None = None
    signal_dependencies: tuple[SignalId, ...] = field(default_factory=tuple)
    variable_dependencies: tuple[VariableId, ...] = field(default_factory=tuple)
    dependency_aliases: Mapping[str, str] = field(default_factory=dict)
    fallback_value: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class VariableSnapshot:
    variable_id: VariableId
    value: str
    quality: SignalQuality
    state: VariableState
    timestamp: EventTime
    dependency_values: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class VariableEvaluationResult:
    snapshot: VariableSnapshot
    resolved_dependencies: Mapping[str, str]
    missing_dependencies: tuple[str, ...] = field(default_factory=tuple)


class _SafeExpressionEvaluator(ast.NodeVisitor):
    _ALLOWED_BINARY = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.Mod: lambda a, b: a % b,
    }
    _ALLOWED_UNARY = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
        ast.Not: lambda a: not a,
    }
    _ALLOWED_COMPARE = {
        ast.Eq: lambda a, b: a == b,
        ast.NotEq: lambda a, b: a != b,
        ast.Gt: lambda a, b: a > b,
        ast.GtE: lambda a, b: a >= b,
        ast.Lt: lambda a, b: a < b,
        ast.LtE: lambda a, b: a <= b,
    }

    def __init__(
        self,
        environment: Mapping[str, object],
        *,
        max_nodes: int = MAX_VARIABLE_EXPRESSION_NODES,
        max_steps: int = MAX_VARIABLE_EVALUATION_STEPS,
        max_power_abs_exponent: int = MAX_VARIABLE_POWER_ABS_EXPONENT,
    ):
        self.environment = environment
        self.max_nodes = max_nodes
        self.max_steps = max_steps
        self.max_power_abs_exponent = max_power_abs_exponent
        self._steps = 0
        self._depth = 0

    @classmethod
    def validate_expression_shape(cls, expression: str, parsed: ast.AST) -> None:
        if len(expression) > MAX_VARIABLE_EXPRESSION_LENGTH:
            raise ValueError('expression length limit exceeded')
        if sum(1 for _ in ast.walk(parsed)) > MAX_VARIABLE_EXPRESSION_NODES:
            raise ValueError('expression node budget exceeded')

    def visit(self, node: ast.AST) -> object:  # type: ignore[override]
        self._steps += 1
        if self._steps > self.max_steps:
            raise ValueError('expression evaluation step budget exceeded')
        self._depth += 1
        if self._depth > self.max_nodes:
            raise ValueError('expression nesting limit exceeded')
        try:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, None)
            if visitor is None:
                raise ValueError(f'unsupported expression node: {node.__class__.__name__}')
            return visitor(node)
        finally:
            self._depth -= 1

    def visit_Expression(self, node: ast.Expression) -> object:
        return self.visit(node.body)

    def visit_Name(self, node: ast.Name) -> object:
        if node.id not in self.environment:
            raise KeyError(node.id)
        return self.environment[node.id]

    def visit_Constant(self, node: ast.Constant) -> object:
        if isinstance(node.value, (int, float, bool, str)):
            return node.value
        raise ValueError('unsupported constant')

    def visit_BinOp(self, node: ast.BinOp) -> object:
        if isinstance(node.op, ast.Pow):
            left = self.visit(node.left)
            right = self.visit(node.right)
            if not isinstance(right, (int, float)):
                raise ValueError('power exponent must be numeric')
            if abs(right) > self.max_power_abs_exponent:
                raise ValueError('power exponent limit exceeded')
            return left ** right
        operator = self._ALLOWED_BINARY.get(type(node.op))
        if operator is None:
            raise ValueError('unsupported binary operator')
        return operator(self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node: ast.UnaryOp) -> object:
        operator = self._ALLOWED_UNARY.get(type(node.op))
        if operator is None:
            raise ValueError('unsupported unary operator')
        return operator(self.visit(node.operand))

    def visit_BoolOp(self, node: ast.BoolOp) -> object:
        values = [bool(self.visit(item)) for item in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        if isinstance(node.op, ast.Or):
            return any(values)
        raise ValueError('unsupported boolean operator')

    def visit_Compare(self, node: ast.Compare) -> object:
        current = self.visit(node.left)
        for operator_node, comparator in zip(node.ops, node.comparators, strict=True):
            operator = self._ALLOWED_COMPARE.get(type(operator_node))
            if operator is None:
                raise ValueError('unsupported compare operator')
            next_value = self.visit(comparator)
            if not operator(current, next_value):
                return False
            current = next_value
        return True

    def visit_IfExp(self, node: ast.IfExp) -> object:
        return self.visit(node.body if bool(self.visit(node.test)) else node.orelse)


def _coerce_dependency_value(value: str) -> object:
    lowered = value.strip().lower()
    if lowered in {'true', 'false'}:
        return lowered == 'true'
    try:
        numeric = float(value)
    except ValueError:
        return value
    if numeric.is_integer():
        return int(numeric)
    return numeric


class VariableEvaluationService:
    def __init__(self, *, metrics: RuntimeMetricsStore | None = None) -> None:
        self.definitions: dict[VariableId, VariableDefinition] = {}
        self.snapshots: dict[VariableId, VariableSnapshot] = {}
        self.signal_dependents: dict[SignalId, set[VariableId]] = {}
        self.variable_dependents: dict[VariableId, set[VariableId]] = {}
        self.metrics = metrics

    def _unindex_definition(self, definition: VariableDefinition) -> None:
        for signal_id in definition.signal_dependencies:
            dependents = self.signal_dependents.get(signal_id)
            if dependents is None:
                continue
            dependents.discard(definition.variable_id)
            if not dependents:
                self.signal_dependents.pop(signal_id, None)
        for variable_id in definition.variable_dependencies:
            dependents = self.variable_dependents.get(variable_id)
            if dependents is None:
                continue
            dependents.discard(definition.variable_id)
            if not dependents:
                self.variable_dependents.pop(variable_id, None)

    def _index_definition(self, definition: VariableDefinition) -> None:
        for signal_id in definition.signal_dependencies:
            self.signal_dependents.setdefault(signal_id, set()).add(definition.variable_id)
        for variable_id in definition.variable_dependencies:
            self.variable_dependents.setdefault(variable_id, set()).add(definition.variable_id)

    def register(self, definition: VariableDefinition) -> None:
        previous = self.definitions.get(definition.variable_id)
        if previous is not None:
            self._unindex_definition(previous)
        self.definitions[definition.variable_id] = definition
        self._index_definition(definition)
        if self.metrics is not None:
            self.metrics.increment('variables.definition.register.calls')
            self.metrics.set_gauge('variables.definition.count', len(self.definitions))

    def publish_snapshot(self, snapshot: VariableSnapshot) -> None:
        self.snapshots[snapshot.variable_id] = snapshot
        if self.metrics is not None:
            self.metrics.increment('variables.snapshot.publish.calls')
            self.metrics.set_gauge('variables.snapshot.count', len(self.snapshots))

    def impacted_variable_ids(
        self,
        *,
        changed_signal_ids: tuple[SignalId, ...] = (),
        changed_variable_ids: tuple[VariableId, ...] = (),
    ) -> tuple[VariableId, ...]:
        impacted: set[VariableId] = set(changed_variable_ids)
        queue = deque(changed_variable_ids)
        for signal_id in changed_signal_ids:
            for variable_id in self.signal_dependents.get(signal_id, set()):
                if variable_id not in impacted:
                    impacted.add(variable_id)
                    queue.append(variable_id)
        while queue:
            current = queue.popleft()
            for dependent in self.variable_dependents.get(current, set()):
                if dependent not in impacted:
                    impacted.add(dependent)
                    queue.append(dependent)
        ordered = tuple(variable_id for variable_id in self.definitions.keys() if variable_id in impacted)
        if self.metrics is not None:
            self.metrics.set_gauge('variables.impacted.count', len(ordered))
        return ordered

    def evaluate_all(
        self,
        *,
        signal_registry: SignalRegistry,
        timestamp: EventTime,
    ) -> tuple[VariableEvaluationResult, ...]:
        return self.evaluate_many(
            tuple(self.definitions.keys()),
            signal_registry=signal_registry,
            timestamp=timestamp,
        )

    def evaluate_impacted(
        self,
        *,
        signal_registry: SignalRegistry,
        timestamp: EventTime,
        changed_signal_ids: tuple[SignalId, ...] = (),
        changed_variable_ids: tuple[VariableId, ...] = (),
    ) -> tuple[VariableEvaluationResult, ...]:
        impacted = self.impacted_variable_ids(
            changed_signal_ids=changed_signal_ids,
            changed_variable_ids=changed_variable_ids,
        )
        if not impacted:
            return ()
        return self.evaluate_many(
            impacted,
            signal_registry=signal_registry,
            timestamp=timestamp,
        )

    def evaluate_many(
        self,
        variable_ids: tuple[VariableId, ...],
        *,
        signal_registry: SignalRegistry,
        timestamp: EventTime,
    ) -> tuple[VariableEvaluationResult, ...]:
        accumulated: dict[VariableId, VariableSnapshot] = dict(self.snapshots)
        results: list[VariableEvaluationResult] = []
        for variable_id in variable_ids:
            result = self.evaluate(
                variable_id,
                signal_registry=signal_registry,
                timestamp=timestamp,
                variable_snapshots=accumulated,
            )
            accumulated[result.snapshot.variable_id] = result.snapshot
            results.append(result)
        if self.metrics is not None:
            self.metrics.set_gauge('variables.last_evaluated.count', len(results))
        return tuple(results)

    def _apply_dependency_quality(self, current: SignalQuality, observed: SignalQuality) -> SignalQuality:
        if observed == SignalQuality.INVALID or current == SignalQuality.INVALID:
            return SignalQuality.INVALID
        if observed == SignalQuality.DISCONNECTED:
            return SignalQuality.DISCONNECTED
        if observed == SignalQuality.STALE:
            return SignalQuality.STALE if current == SignalQuality.GOOD else current
        return current

    def _build_environment(
        self,
        *,
        definition: VariableDefinition,
        signal_registry: SignalRegistry,
        variable_snapshots: Mapping[VariableId, VariableSnapshot] | None,
    ) -> tuple[dict[str, object], dict[str, str], tuple[str, ...], SignalQuality]:
        alias_map: dict[str, object] = {}
        resolved: dict[str, str] = {}
        missing: list[str] = []
        quality = SignalQuality.GOOD
        variable_snapshot_map = variable_snapshots or self.snapshots

        for signal_id in definition.signal_dependencies:
            alias = definition.dependency_aliases.get(str(signal_id), str(signal_id))
            snapshot = signal_registry.snapshots.get(signal_id)
            if snapshot is None:
                missing.append(alias)
                quality = SignalQuality.INVALID
                continue
            alias_map[alias] = _coerce_dependency_value(snapshot.value)
            resolved[alias] = snapshot.value
            quality = self._apply_dependency_quality(quality, snapshot.quality)

        for variable_id in definition.variable_dependencies:
            alias = definition.dependency_aliases.get(str(variable_id), str(variable_id))
            snapshot = variable_snapshot_map.get(variable_id)
            if snapshot is None:
                missing.append(alias)
                quality = SignalQuality.INVALID
                continue
            alias_map[alias] = _coerce_dependency_value(snapshot.value)
            resolved[alias] = snapshot.value
            observed_quality = snapshot.quality
            if snapshot.state == VariableState.DEGRADED:
                observed_quality = SignalQuality.DISCONNECTED
            elif snapshot.state == VariableState.UNRESOLVED:
                observed_quality = SignalQuality.INVALID
            quality = self._apply_dependency_quality(quality, observed_quality)

        return alias_map, resolved, tuple(missing), quality

    def evaluate(
        self,
        variable_id: VariableId,
        *,
        signal_registry: SignalRegistry,
        timestamp: EventTime,
        variable_snapshots: Mapping[VariableId, VariableSnapshot] | None = None,
    ) -> VariableEvaluationResult:
        if self.metrics is not None:
            self.metrics.increment('variables.evaluate.calls')
            with self.metrics.measure('variables.evaluate.ms'):
                result = self._evaluate_impl(
                    variable_id=variable_id,
                    signal_registry=signal_registry,
                    timestamp=timestamp,
                    variable_snapshots=variable_snapshots,
                )
            self.metrics.set_gauge('variables.snapshot.count', len(self.snapshots))
            return result
        return self._evaluate_impl(
            variable_id=variable_id,
            signal_registry=signal_registry,
            timestamp=timestamp,
            variable_snapshots=variable_snapshots,
        )

    def _evaluate_impl(
        self,
        *,
        variable_id: VariableId,
        signal_registry: SignalRegistry,
        timestamp: EventTime,
        variable_snapshots: Mapping[VariableId, VariableSnapshot] | None,
    ) -> VariableEvaluationResult:
        definition = self.definitions[variable_id]
        environment, resolved, missing, dependency_quality = self._build_environment(
            definition=definition,
            signal_registry=signal_registry,
            variable_snapshots=variable_snapshots,
        )

        state = VariableState.HEALTHY
        quality = dependency_quality
        value: object | str

        if definition.source_kind == VariableSourceKind.CONSTANT:
            value = '' if definition.constant_value is None else definition.constant_value
        elif definition.source_kind == VariableSourceKind.SIGNAL:
            if len(definition.signal_dependencies) != 1:
                raise ValueError('signal variables must declare exactly one signal dependency')
            dependency_alias = definition.dependency_aliases.get(
                str(definition.signal_dependencies[0]),
                str(definition.signal_dependencies[0]),
            )
            if dependency_alias not in resolved:
                if definition.fallback_value is not None:
                    value = definition.fallback_value
                    state = VariableState.SUBSTITUTED
                    quality = SignalQuality.STALE
                else:
                    value = ''
                    state = VariableState.UNRESOLVED
                    quality = SignalQuality.INVALID
            else:
                value = resolved[dependency_alias]
        elif definition.source_kind == VariableSourceKind.VARIABLE:
            if len(definition.variable_dependencies) != 1:
                raise ValueError('variable-alias definitions must declare exactly one variable dependency')
            dependency_alias = definition.dependency_aliases.get(
                str(definition.variable_dependencies[0]),
                str(definition.variable_dependencies[0]),
            )
            if dependency_alias not in resolved:
                if definition.fallback_value is not None:
                    value = definition.fallback_value
                    state = VariableState.SUBSTITUTED
                    quality = SignalQuality.STALE
                else:
                    value = ''
                    state = VariableState.UNRESOLVED
                    quality = SignalQuality.INVALID
            else:
                value = resolved[dependency_alias]
        else:
            if missing and definition.fallback_value is not None:
                value = definition.fallback_value
                state = VariableState.SUBSTITUTED
                quality = SignalQuality.STALE
            else:
                try:
                    expression = '' if definition.expression is None else definition.expression
                    parsed = ast.parse(expression, mode='eval')
                    _SafeExpressionEvaluator.validate_expression_shape(expression, parsed)
                    value = _SafeExpressionEvaluator(environment).visit(parsed)
                except KeyError as exc:
                    missing = tuple(sorted(set(missing + (str(exc.args[0]),))))
                    value = '' if definition.fallback_value is None else definition.fallback_value
                    if definition.fallback_value is None:
                        state = VariableState.UNRESOLVED
                        quality = SignalQuality.INVALID
                    else:
                        state = VariableState.SUBSTITUTED
                        quality = SignalQuality.STALE
                except Exception:
                    value = ''
                    state = VariableState.INVALID
                    quality = SignalQuality.INVALID

        if state == VariableState.HEALTHY:
            if quality == SignalQuality.INVALID:
                state = VariableState.INVALID if not missing else VariableState.UNRESOLVED
            elif quality == SignalQuality.DISCONNECTED:
                state = VariableState.DEGRADED
            elif quality == SignalQuality.STALE:
                state = VariableState.STALE

        snapshot = VariableSnapshot(
            variable_id=variable_id,
            value=str(value),
            quality=quality,
            state=state,
            timestamp=timestamp,
            dependency_values=resolved,
        )
        self.publish_snapshot(snapshot)
        return VariableEvaluationResult(snapshot=snapshot, resolved_dependencies=resolved, missing_dependencies=missing)
