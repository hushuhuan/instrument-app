from __future__ import annotations

from instrument_app.domain.app_config import AppConfig, ApplicationRunMode
from instrument_app.domain.selftest.self_test_orchestrator import run_self_test
from instrument_app.hal.mock.mock_instrument_hal import MockInstrumentHal


def test_run_self_test_mock_all_pass() -> None:
    cfg = AppConfig()
    cfg.run_mode = ApplicationRunMode.MOCK
    hal = MockInstrumentHal()
    report = run_self_test(cfg, hal)
    assert report["schemaVersion"] == 1
    assert report["overallPass"] is True
    assert len(report["items"]) == 6
    assert all(it["status"] == "passed" for it in report["items"])
    ids = [it["stepId"] for it in report["items"]]
    assert ids == [
        "Network",
        "DiskSpace",
        "PumpInit",
        "RotaryValveInit",
        "StepperHome",
        "ChillerComm",
    ]


def test_run_self_test_skips_hal_after_network_fail(monkeypatch) -> None:
    cfg = AppConfig()
    cfg.run_mode = ApplicationRunMode.MOCK
    hal = MockInstrumentHal()

    def boom() -> tuple[bool, str]:
        return False, "network down"

    monkeypatch.setattr(
        "instrument_app.domain.selftest.self_test_orchestrator.check_network",
        boom,
    )
    report = run_self_test(cfg, hal)
    assert report["overallPass"] is False
    assert report["items"][0]["status"] == "failed"
    assert report["items"][1]["status"] == "not_run"
