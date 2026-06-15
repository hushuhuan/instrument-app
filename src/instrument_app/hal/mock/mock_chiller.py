from __future__ import annotations

from instrument_app.hal.mock import mock_test_hooks as th


class MockChillerSubsystem:
    def __init__(self) -> None:
        self._debug_setpoint: float | None = None
        self._last_handshake_ok: bool | None = None

    def chiller_handshake(self) -> tuple[bool, str]:
        hooked = th.peek_chiller_failure()
        if hooked is not None:
            self._last_handshake_ok = False
            return hooked
        self._last_handshake_ok = True
        return True, "Mock: chiller handshake OK"

    def debug_chiller_set_setpoint(self, setpoint_celsius: float) -> tuple[bool, str]:
        if not th.allow_hal_debug_commands():
            return False, "HAL 调试命令已禁用（设置 INSTRUMENT_HAL_DEBUG=1）"
        self._debug_setpoint = setpoint_celsius
        return True, f"Mock: chiller setpoint {setpoint_celsius:.1f} °C"

    def debug_chiller_read_setpoint(self) -> tuple[float | None, str]:
        if not th.allow_hal_debug_commands():
            return None, "HAL 调试命令已禁用（设置 INSTRUMENT_HAL_DEBUG=1）"
        if self._debug_setpoint is None:
            return None, "Mock: no setpoint written yet"
        return self._debug_setpoint, f"Mock: readback {self._debug_setpoint:.1f} °C"

    def health_row(self) -> tuple[str, bool, str]:
        if self._last_handshake_ok is None:
            return "温控/冷机", True, "仿真就绪（尚未记录握手结果）"
        return (
            "温控/冷机",
            self._last_handshake_ok,
            "最近一次握手成功" if self._last_handshake_ok else "最近一次握手失败",
        )
