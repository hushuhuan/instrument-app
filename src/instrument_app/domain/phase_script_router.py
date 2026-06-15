from __future__ import annotations

from instrument_app.domain.app_config import AppConfig
from instrument_app.domain.recipe_models import BusinessPhase, RecipeStep
from instrument_app.hal.interfaces.instrument_hal import InstrumentHal


def step_duration_ms(step: RecipeStep, cfg: AppConfig, hal: InstrumentHal) -> int:
    scale = max(1, cfg.mock_time_scale)
    sec = max(1, min(86400, step.plan_duration_sec))

    if step.business_phase == BusinessPhase.REACTION:
        return max(
            250,
            hal.simulate_reaction_step_ms(sec, cfg.mock_time_scale),
        )

    # Other business phases: scaled wall-clock mock; can later branch per phase for HAL.
    ms = (sec * 1000) // scale
    return max(250, ms)
