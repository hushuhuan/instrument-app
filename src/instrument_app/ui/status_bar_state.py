from __future__ import annotations

from typing import Any

from instrument_app.domain.run_models import RunSessionPhase
from instrument_app.hal.interfaces.instrument_hal import InstrumentHal


def _run_phase_schema(p: RunSessionPhase) -> str:
    return {
        RunSessionPhase.IDLE: "Idle",
        RunSessionPhase.RUNNING: "Running",
        RunSessionPhase.PAUSED: "Paused",
        RunSessionPhase.FAILED: "Failed",
        RunSessionPhase.COMPLETED: "Completed",
    }[p]


def _remaining_fields(
    phase: RunSessionPhase, remaining_sec: int
) -> tuple[str, int | None]:
    if phase == RunSessionPhase.RUNNING:
        return "countdown", max(0, int(remaining_sec))
    if phase == RunSessionPhase.PAUSED:
        return "paused", max(0, int(remaining_sec))
    if phase == RunSessionPhase.IDLE:
        return "idle", None
    if phase == RunSessionPhase.COMPLETED:
        return "idle", 0
    if phase == RunSessionPhase.FAILED:
        return "idle", None
    return "unknown", None


def snapshot_status_bar_state(
    hal: InstrumentHal,
    phase: RunSessionPhase,
    current_action: str,
    remaining_seconds: int,
    use_fahrenheit: bool,
) -> dict[str, Any]:
    """
    Build a document matching ``contracts/status-bar-state.schema.json`` (Phase 9 / T056).
    """
    a = hal.ambient_reading()
    env_ok = bool(a.valid and a.timestamp is not None)
    if use_fahrenheit:
        unit = "F"
        disp_val: float | None = None
        if env_ok:
            disp_val = round(a.temperature_celsius * 9.0 / 5.0 + 32.0, 1)
    else:
        unit = "C"
        disp_val = None
        if env_ok:
            disp_val = round(a.temperature_celsius, 1)

    humid_pct: float | None = None
    if env_ok:
        humid_pct = round(a.humidity_rh, 1)

    r_mode, r_sec = _remaining_fields(phase, remaining_seconds)
    action = current_action.strip() if current_action.strip() else "空闲"

    return {
        "refreshIntervalMs": 1000,
        "temperature": {
            "displayValue": disp_val,
            "displayUnit": unit,
            "valid": env_ok,
        },
        "humidityRh": {
            "valuePercent": humid_pct,
            "valid": env_ok,
        },
        "currentAction": action,
        "remainingTime": {"mode": r_mode, "seconds": r_sec},
        "runPhase": _run_phase_schema(phase),
    }
