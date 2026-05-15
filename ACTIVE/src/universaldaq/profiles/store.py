from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from universaldaq.common import ProfileId

from .models import BenchPersistenceState, PersistedSessionSummary, ProfileSnapshot
from .serializers import (
    deserialize_bench_persistence_state,
    deserialize_persisted_session_summary,
    deserialize_profile_snapshot,
    serialize_bench_persistence_state,
    serialize_persisted_session_summary,
    serialize_profile_snapshot,
)


@dataclass(slots=True)
class InMemoryProfileStore:
    snapshots: dict[ProfileId, ProfileSnapshot] = field(default_factory=dict)

    def save(self, snapshot: ProfileSnapshot) -> None:
        self.snapshots[snapshot.profile_id] = snapshot

    def load(self, profile_id: ProfileId) -> ProfileSnapshot:
        return self.snapshots[profile_id]


@dataclass(frozen=True, slots=True, kw_only=True)
class FileProfileStore:
    root: Path

    def path_for(self, profile_id: ProfileId) -> Path:
        return self.root / f'{profile_id}.json'

    def save(self, snapshot: ProfileSnapshot) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.path_for(snapshot.profile_id)
        path.write_text(json.dumps(serialize_profile_snapshot(snapshot), indent=2), encoding='utf-8')
        return path

    def load(self, profile_id: ProfileId) -> ProfileSnapshot:
        path = self.path_for(profile_id)
        payload = json.loads(path.read_text(encoding='utf-8'))
        return deserialize_profile_snapshot(payload)


@dataclass(slots=True)
class InMemoryBenchStateStore:
    state: BenchPersistenceState | None = None
    summaries: dict[str, PersistedSessionSummary] = field(default_factory=dict)

    def save_state(self, state: BenchPersistenceState) -> None:
        self.state = state
        if state.historical_summary is not None:
            self.summaries[state.historical_summary.summary_id] = state.historical_summary

    def load_state(self) -> BenchPersistenceState:
        if self.state is None:
            raise KeyError('no bench persistence state saved')
        return self.state

    def save_summary(self, summary: PersistedSessionSummary) -> None:
        self.summaries[summary.summary_id] = summary

    def load_summary(self, summary_id: str) -> PersistedSessionSummary:
        return self.summaries[summary_id]

    def list_recent_summaries(self, *, limit: int = 5) -> tuple[PersistedSessionSummary, ...]:
        ordered = sorted(self.summaries.values(), key=lambda item: int(item.saved_at))
        return tuple(ordered[-max(1, limit):])


@dataclass(frozen=True, slots=True, kw_only=True)
class FileBenchStateStore:
    root: Path
    state_filename: str = 'bench_state.json'
    summary_dirname: str = 'session_summaries'

    @property
    def state_path(self) -> Path:
        return self.root / self.state_filename

    @property
    def summary_root(self) -> Path:
        return self.root / self.summary_dirname

    def summary_path_for(self, summary_id: str) -> Path:
        return self.summary_root / f'{summary_id}.json'

    def save_state(self, state: BenchPersistenceState) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(serialize_bench_persistence_state(state), indent=2), encoding='utf-8')
        if state.historical_summary is not None:
            self.save_summary(state.historical_summary)
        return self.state_path

    def load_state(self) -> BenchPersistenceState:
        payload = json.loads(self.state_path.read_text(encoding='utf-8'))
        return deserialize_bench_persistence_state(payload)

    def save_summary(self, summary: PersistedSessionSummary) -> Path:
        self.summary_root.mkdir(parents=True, exist_ok=True)
        path = self.summary_path_for(summary.summary_id)
        path.write_text(json.dumps(serialize_persisted_session_summary(summary), indent=2), encoding='utf-8')
        return path

    def load_summary(self, summary_id: str) -> PersistedSessionSummary:
        payload = json.loads(self.summary_path_for(summary_id).read_text(encoding='utf-8'))
        return deserialize_persisted_session_summary(payload)

    def list_recent_summaries(self, *, limit: int = 5) -> tuple[PersistedSessionSummary, ...]:
        if not self.summary_root.exists():
            return ()
        ordered = sorted(self.summary_root.glob('*.json'))
        summaries = [deserialize_persisted_session_summary(json.loads(path.read_text(encoding='utf-8'))) for path in ordered]
        summaries.sort(key=lambda item: int(item.saved_at))
        return tuple(summaries[-max(1, limit):])
