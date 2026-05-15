from __future__ import annotations

from .dependency_graph import validate_derived_signals
from .models import DerivedSignalDefinition


def validate_for_activation(definitions: tuple[DerivedSignalDefinition, ...]):
    return validate_derived_signals(definitions)
