from __future__ import annotations

import os
from dataclasses import dataclass


def test_hooks_enabled() -> bool:
    return os.environ.get("INSTRUMENT_TEST_HOOKS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def allow_hal_debug_commands() -> bool:
    """Debug pump/valve/chiller commands (bench UI). Default allow; set INSTRUMENT_HAL_DEBUG=0 to hard-disable."""
    v = os.environ.get("INSTRUMENT_HAL_DEBUG", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


@dataclass
class MockTestHookState:
    """Mutable flags consulted only when ``INSTRUMENT_TEST_HOOKS`` is enabled (T041)."""

    fail_pump_init: bool = False
    fail_valve_init: bool = False
    fail_stepper_home: bool = False
    fail_chiller_handshake: bool = False
    deny_hal_debug: bool = False


_state = MockTestHookState()


def hook_state() -> MockTestHookState:
    return _state


def reset_hooks() -> None:
    global _state
    _state = MockTestHookState()


def peek_pump_init_failure() -> tuple[bool, str] | None:
    if not test_hooks_enabled() or not _state.fail_pump_init:
        return None
    return False, "Mock test hook: pump init forced failure"


def peek_valve_init_failure() -> tuple[bool, str] | None:
    if not test_hooks_enabled() or not _state.fail_valve_init:
        return None
    return False, "Mock test hook: rotary valve init forced failure"


def peek_stepper_failure() -> tuple[bool, str] | None:
    if not test_hooks_enabled() or not _state.fail_stepper_home:
        return None
    return False, "Mock test hook: stepper home forced failure"


def peek_chiller_failure() -> tuple[bool, str] | None:
    if not test_hooks_enabled() or not _state.fail_chiller_handshake:
        return None
    return False, "Mock test hook: chiller handshake forced failure"


def peek_debug_denied() -> bool:
    return test_hooks_enabled() and _state.deny_hal_debug
