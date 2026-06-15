from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from instrument_app.domain.phase_script_router import step_duration_ms
from instrument_app.domain.recipe_models import BusinessPhase, ProcessParameters, Recipe, RecipeStep

from instrument_app.domain.app_config import AppConfig, ApplicationRunMode
from instrument_app.hal.mock.mock_instrument_hal import MockInstrumentHal
from instrument_app.persistence.recipe_repository import load_recipe_json, save_recipe_json


def test_recipe_json_roundtrip(tmp_path) -> None:
    params = ProcessParameters(solvent="丙酮", reaction_time_sec=200)
    steps = [
        RecipeStep(
            uuid4(), 0, BusinessPhase.POWDER, 60, {}, ""
        ),
        RecipeStep(
            uuid4(),
            1,
            BusinessPhase.REACTION,
            120,
            {"temperatureC": 80.0},
            "自定义显示",
        ),
    ]
    recipe = Recipe(
        uuid4(),
        "试运行配方",
        datetime.now(timezone.utc),
        params,
        steps,
    )
    path = tmp_path / "recipe.json"
    save_recipe_json(path, recipe)
    back = load_recipe_json(path)
    assert back.name == recipe.name
    assert back.parameters.solvent == "丙酮"
    assert len(back.steps) == 2
    assert back.steps[1].business_phase == BusinessPhase.REACTION
    assert back.steps[1].display_override == "自定义显示"


def test_step_duration_ms_all_phases_use_hal_for_reaction() -> None:
    cfg = AppConfig()
    cfg.run_mode = ApplicationRunMode.MOCK
    cfg.mock_time_scale = 10
    hal = MockInstrumentHal(mock_time_scale_divisor=10)
    r = RecipeStep(uuid4(), 0, BusinessPhase.REACTION, 100, {}, "")
    d = step_duration_ms(r, cfg, hal)
    assert d >= 250
    p = RecipeStep(uuid4(), 0, BusinessPhase.POWDER, 10, {}, "")
    d2 = step_duration_ms(p, cfg, hal)
    assert d2 >= 250
