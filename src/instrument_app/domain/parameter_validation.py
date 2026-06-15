from __future__ import annotations

from instrument_app.domain.recipe_models import ProcessParameters


def validate_for_ready(p: ProcessParameters) -> list[str]:
    errors: list[str] = []
    if p.reaction_time_sec < 1 or p.reaction_time_sec > 86400:
        errors.append("反应时间须在 1–86400 秒内")
    if p.stir_speed_rpm < 0 or p.stir_speed_rpm > 2000:
        errors.append("搅拌速度须在 0–2000 rpm")
    if p.reaction_temp_c < -40.0 or p.reaction_temp_c > 250.0:
        errors.append("反应温度须在 -40–250 ℃")
    if p.sample_count < 0 or p.sample_count > 100:
        errors.append("取样数量须在 0–100")
    if not p.solvent.strip():
        errors.append("溶剂为必填项")
    return errors


def validate_reaction_task_minimal(p: ProcessParameters) -> list[str]:
    errors: list[str] = []
    if p.reaction_time_sec < 1 or p.reaction_time_sec > 86400:
        errors.append("反应时间须在 1–86400 秒内")
    if p.reaction_temp_c < -40.0 or p.reaction_temp_c > 250.0:
        errors.append("反应温度须在 -40–250 ℃")
    if p.stir_speed_rpm < 0 or p.stir_speed_rpm > 2000:
        errors.append("搅拌速度须在 0–2000 rpm")
    return errors
