from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

from instrument_app.domain.recipe_models import (
    BusinessPhase,
    ProcessParameters,
    Recipe,
    RecipeStep,
)


def recipe_from_reaction_task(params: ProcessParameters) -> Recipe:
    step = RecipeStep(
        step_uid=uuid4(),
        order_index=0,
        business_phase=BusinessPhase.REACTION,
        plan_duration_sec=params.reaction_time_sec,
        device_args={
            "temperatureC": params.reaction_temp_c,
            "stirSpeedRpm": params.stir_speed_rpm,
        },
    )
    return Recipe(
        id=uuid4(),
        name="反应任务",
        revision_at=datetime.now(timezone.utc),
        parameters=params,
        steps=[step],
    )


def recipe_from_editor_steps(
    name: str, params: ProcessParameters, steps: list[RecipeStep]
) -> Recipe:
    """Build a Recipe from editor steps; normalize order indices and reaction durations."""
    normalized: list[RecipeStep] = []
    for i, s in enumerate(steps):
        dur = s.plan_duration_sec
        if s.business_phase == BusinessPhase.REACTION and dur < 1:
            dur = max(1, params.reaction_time_sec)
        normalized.append(
            replace(
                s,
                order_index=i,
                plan_duration_sec=max(1, min(86400, dur)),
            )
        )
    return Recipe(
        id=uuid4(),
        name=name.strip() or "未命名方法",
        revision_at=datetime.now(timezone.utc),
        parameters=params,
        steps=normalized,
    )
