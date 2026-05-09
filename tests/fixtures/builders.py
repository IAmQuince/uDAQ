from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass(slots=True)
class FakeRecord:
    kind: str
    payload: Dict[str, Any] = field(default_factory=dict)

def build_record(kind: str, **payload: Any) -> FakeRecord:
    return FakeRecord(kind=kind, payload=payload)
