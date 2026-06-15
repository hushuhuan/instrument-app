from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from instrument_app.domain.recipe_models import (
    BusinessPhase,
    ProcessParameters,
    Recipe,
    RecipeStep,
)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)


def recipe_to_doc(recipe: Recipe) -> dict[str, Any]:
    return {
        "id": str(recipe.id),
        "name": recipe.name,
        "revision_at": _iso(recipe.revision_at),
        "parameters": asdict(recipe.parameters),
        "steps": [step_to_doc(s) for s in recipe.steps],
    }


def step_to_doc(step: RecipeStep) -> dict[str, Any]:
    return {
        "step_uid": str(step.step_uid),
        "order_index": step.order_index,
        "business_phase": step.business_phase.name,
        "plan_duration_sec": step.plan_duration_sec,
        "device_args": step.device_args,
        "display_override": step.display_override,
    }


def recipe_from_doc(data: dict[str, Any]) -> Recipe:
    params_raw = data.get("parameters") or {}
    params = ProcessParameters(**params_raw)
    steps_in = data.get("steps") or []
    steps: list[RecipeStep] = [step_from_doc(s) for s in steps_in]
    return Recipe(
        id=UUID(str(data["id"])),
        name=str(data.get("name") or "导入方法"),
        revision_at=_parse_iso(str(data["revision_at"])),
        parameters=params,
        steps=steps,
    )


def step_from_doc(data: dict[str, Any]) -> RecipeStep:
    phase = BusinessPhase[str(data["business_phase"])]
    return RecipeStep(
        step_uid=UUID(str(data["step_uid"])),
        order_index=int(data.get("order_index", 0)),
        business_phase=phase,
        plan_duration_sec=int(data["plan_duration_sec"]),
        device_args=dict(data.get("device_args") or {}),
        display_override=str(data.get("display_override") or ""),
    )


def save_recipe_json(path: Path, recipe: Recipe) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(recipe_to_doc(recipe), ensure_ascii=False, indent=2)
    path.write_text(text, encoding="utf-8")


def load_recipe_json(path: Path) -> Recipe:
    raw = path.read_text(encoding="utf-8")
    return recipe_from_doc(json.loads(raw))
