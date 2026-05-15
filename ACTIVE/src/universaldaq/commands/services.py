from __future__ import annotations

from dataclasses import dataclass, field

from universaldaq.common import RuntimeMetricsStore

from .models import CommandRecord


@dataclass(slots=True)
class CommandAdmissionService:
    records: list[CommandRecord] = field(default_factory=list)
    metrics: RuntimeMetricsStore | None = None

    def append(self, record: CommandRecord) -> CommandRecord:
        self.records.append(record)
        if self.metrics is not None:
            self.metrics.increment('commands.records.append.calls')
            self.metrics.set_gauge('commands.records.count', len(self.records))
            self.metrics.set_gauge('commands.rejected.count', sum(1 for item in self.records if item.rejected))
            self.metrics.set_gauge('commands.admitted.count', sum(1 for item in self.records if item.admitted))
            self.metrics.set_gauge('commands.dry_run.count', sum(1 for item in self.records if item.intent.dry_run))
        return record

    def summary(self) -> dict[str, object]:
        admitted = [item for item in self.records if item.admitted]
        rejected = [item for item in self.records if item.rejected]
        return {
            'command_count': len(self.records),
            'admitted_count': len(admitted),
            'rejected_count': len(rejected),
            'dry_run_count': sum(1 for item in self.records if item.intent.dry_run),
            'last_command_id': None if not self.records else self.records[-1].intent.command_id,
            'last_rejection_code': None if not rejected else rejected[-1].rejection_code.value,
        }

    def recent_rows(self, *, limit: int = 16) -> tuple[dict[str, object], ...]:
        rows = [item.as_dict() for item in self.records]
        return tuple(rows[-max(1, limit):])
