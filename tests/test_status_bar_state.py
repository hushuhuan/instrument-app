from __future__ import annotations

from instrument_app.domain.app_config import AppConfig
from instrument_app.domain.run_coordinator import RunCoordinator
from instrument_app.domain.run_models import RunSessionPhase
from instrument_app.hal.mock.mock_instrument_hal import MockInstrumentHal
from instrument_app.ui.status_bar_state import snapshot_status_bar_state


def test_status_snapshot_matches_schema_shape() -> None:
    cfg = AppConfig()
    hal = MockInstrumentHal()
    rc = RunCoordinator(cfg, hal)
    d = snapshot_status_bar_state(hal, rc.phase(), "空闲", 0, False)
    assert d["refreshIntervalMs"] == 1000
    assert set(d.keys()) == {
        "refreshIntervalMs",
        "temperature",
        "humidityRh",
        "currentAction",
        "remainingTime",
        "runPhase",
    }
    assert d["temperature"]["displayUnit"] in ("C", "F")
    assert d["runPhase"] in (
        "Idle",
        "Running",
        "Paused",
        "Failed",
        "Completed",
    )
    assert d["remainingTime"]["mode"] in (
        "countdown",
        "paused",
        "idle",
        "unknown",
    )


def test_running_countdown_seconds() -> None:
    cfg = AppConfig()
    hal = MockInstrumentHal()
    d = snapshot_status_bar_state(hal, RunSessionPhase.RUNNING, "反应", 125, False)
    assert d["remainingTime"]["mode"] == "countdown"
    assert d["remainingTime"]["seconds"] == 125
    assert d["currentAction"] == "反应"
