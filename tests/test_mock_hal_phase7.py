from __future__ import annotations

import json

import pytest

from instrument_app.hal.mock import mock_test_hooks as th
from instrument_app.hal.mock.mock_instrument_hal import MockInstrumentHal


def test_mock_hal_composed_modules_device_health() -> None:
    hal = MockInstrumentHal()
    rows = hal.device_health_summary()
    assert len(rows) == 5
    assert all(ok for _, ok, _ in rows)


def test_test_hooks_pump_init_failure(monkeypatch) -> None:
    monkeypatch.setenv("INSTRUMENT_TEST_HOOKS", "1")
    th.reset_hooks()
    th.hook_state().fail_pump_init = True
    hal = MockInstrumentHal()
    ok, msg = hal.init_pumps()
    assert ok is False
    assert "test hook" in msg.lower() or "强制" in msg or "forced" in msg.lower()


def test_hal_debug_disabled_env(monkeypatch) -> None:
    monkeypatch.setenv("INSTRUMENT_HAL_DEBUG", "0")
    hal = MockInstrumentHal()
    ok, msg = hal.debug_pump_command("stop", 1.0)
    assert ok is False
    assert "禁用" in msg or "INSTRUMENT_HAL_DEBUG" in msg


def test_test_hook_deny_debug(monkeypatch) -> None:
    monkeypatch.setenv("INSTRUMENT_TEST_HOOKS", "1")
    th.reset_hooks()
    th.hook_state().deny_hal_debug = True
    hal = MockInstrumentHal()
    ok, msg = hal.debug_pump_command("stop", 1.0)
    assert ok is False
