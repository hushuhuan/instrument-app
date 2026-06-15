from __future__ import annotations

from instrument_app.hal.mock import mock_test_hooks as th


class MockRotaryValveSubsystem:
    def __init__(self) -> None:
        self._debug_channel = 0
        self._last_init_ok: bool | None = None

    def init_rotary_valve(self) -> tuple[bool, str]:
        hooked = th.peek_valve_init_failure()
        if hooked is not None:
            self._last_init_ok = False
            return hooked
        self._last_init_ok = True
        return True, "Mock: rotary valve initialized"

    def debug_rotary_valve_goto_channel(self, channel: int) -> tuple[bool, str]:
        if not th.allow_hal_debug_commands():
            return False, "HAL 调试命令已禁用（设置 INSTRUMENT_HAL_DEBUG=1）"
        if channel < 0 or channel > 15:
            return False, "Mock: channel out of range 0–15"
        self._debug_channel = channel
        return True, f"Mock: valve at channel {channel}"

    def health_row(self) -> tuple[str, bool, str]:
        if self._last_init_ok is None:
            return "旋转阀", True, "仿真就绪（尚未记录初始化结果）"
        return (
            "旋转阀",
            self._last_init_ok,
            "最近一次初始化成功" if self._last_init_ok else "最近一次初始化失败",
        )
