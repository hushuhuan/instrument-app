from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any
from uuid import UUID


class BusinessPhase(Enum):
    POWDER = auto()
    REACTION = auto()
    EXTRACTION = auto()
    DISTILLATION = auto()
    FILTRATION = auto()
    SAMPLING = auto()


def business_phase_label(p: BusinessPhase) -> str:
    return {
        BusinessPhase.POWDER: "加粉",
        BusinessPhase.REACTION: "反应",
        BusinessPhase.EXTRACTION: "萃取",
        BusinessPhase.DISTILLATION: "蒸馏",
        BusinessPhase.FILTRATION: "过滤",
        BusinessPhase.SAMPLING: "取样",
    }.get(p, "未知阶段")


def step_status_line(step: RecipeStep) -> str:
    """Status bar / progress label; honors display_override per data model."""
    o = step.display_override.strip()
    if o:
        return o
    return business_phase_label(step.business_phase)


@dataclass
class ProcessParameters:
    reaction_time_sec: int = 300
    stir_speed_rpm: int = 200
    reaction_temp_c: float = 25.0
    rinse_params: str = ""
    solvent: str = ""
    extraction_params: str = ""
    filtration_params: str = ""
    sample_count: int = 1


@dataclass
class RecipeStep:
    step_uid: UUID
    order_index: int
    business_phase: BusinessPhase
    plan_duration_sec: int
    device_args: dict[str, Any] = field(default_factory=dict)
    display_override: str = ""


@dataclass
class Recipe:
    id: UUID
    name: str
    revision_at: datetime
    parameters: ProcessParameters
    steps: list[RecipeStep]
