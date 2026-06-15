from __future__ import annotations

from instrument_app.hal.mock import mock_test_hooks as th


class MockPumpSubsystem:
    def __init__(self) -> None:
        self._debug_action = "stop"
        self._last_init_ok: bool | None = None

    def init_pumps(self) -> tuple[bool, str]:
        hooked = th.peek_pump_init_failure()
        if hooked is not None:
            self._last_init_ok = False
            return hooked
        self._last_init_ok = True
        return True, "Mock: pumps initialized"

    def debug_pump_command(self, action: str, flow_ul_per_min: float) -> tuple[bool, str]:
        if not th.allow_hal_debug_commands():
            return False, "HAL 调试命令已禁用（设置 INSTRUMENT_HAL_DEBUG=1）"
        if th.peek_debug_denied():
            return False, "Mock test hook: debug denied"
        a = action.strip().lower()
        if a == "prime":
            self._debug_action = "prime"
            return True, f"Mock: pump prime OK (flow param={flow_ul_per_min})"
        if a == "dispense":
            self._debug_action = f"dispense@{flow_ul_per_min}uL/min"
            return True, f"Mock: pump dispensing at {flow_ul_per_min} µL/min"
        if a == "stop":
            self._debug_action = "stop"
            return True, "Mock: pump stop OK"
        return False, f"Mock: unknown pump action {action!r}"

    def health_row(self) -> tuple[str, bool, str]:
        if self._last_init_ok is None:
            return "注射泵", True, "仿真就绪（尚未记录初始化结果）"
        return (
            "注射泵",
            self._last_init_ok,
            "最近一次初始化成功" if self._last_init_ok else "最近一次初始化失败",
        )
