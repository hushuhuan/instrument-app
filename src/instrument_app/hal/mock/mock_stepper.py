from __future__ import annotations

from instrument_app.hal.mock import mock_test_hooks as th


class MockStepperSubsystem:
    def __init__(self) -> None:
        self._last_home_ok: bool | None = None

    def home_stepper(self) -> tuple[bool, str]:
        hooked = th.peek_stepper_failure()
        if hooked is not None:
            self._last_home_ok = False
            return hooked
        self._last_home_ok = True
        return True, "Mock: stepper homed"

    def health_row(self) -> tuple[str, bool, str]:
        if self._last_home_ok is None:
            return "步进轴", True, "仿真就绪（尚未记录回零结果）"
        return (
            "步进轴",
            self._last_home_ok,
            "最近一次回零成功" if self._last_home_ok else "最近一次回零失败",
        )
