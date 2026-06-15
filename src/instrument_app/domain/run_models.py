from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from uuid import UUID


class RunSessionPhase(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FAILED = auto()
    COMPLETED = auto()


def run_session_phase_label(p: RunSessionPhase) -> str:
    return {
        RunSessionPhase.IDLE: "空闲",
        RunSessionPhase.RUNNING: "运行中",
        RunSessionPhase.PAUSED: "已暂停",
        RunSessionPhase.FAILED: "失败",
        RunSessionPhase.COMPLETED: "已完成",
    }.get(p, "?")


@dataclass
class RunState:
    id: UUID | None = None
    recipe_id: UUID | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    phase: RunSessionPhase = RunSessionPhase.IDLE
    current_step_index: int = 0
    step_statuses: list[str] = field(default_factory=list)
