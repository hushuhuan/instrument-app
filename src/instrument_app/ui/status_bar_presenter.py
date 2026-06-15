from __future__ import annotations

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QLabel, QStatusBar

from instrument_app.domain.run_coordinator import RunCoordinator
from instrument_app.domain.run_models import RunSessionPhase
from instrument_app.hal.interfaces.instrument_hal import InstrumentHal
from instrument_app.ui.status_bar_state import snapshot_status_bar_state


class StatusBarPresenter(QObject):
    def __init__(
        self,
        hal: InstrumentHal,
        runs: RunCoordinator,
        bar: QStatusBar,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._hal = hal
        self._runs = runs
        self._env = QLabel(bar)
        self._action = QLabel(bar)
        self._eta = QLabel(bar)
        bar.addWidget(self._env, 1)
        bar.addWidget(self._action, 1)
        bar.addWidget(self._eta, 1)
        self._current_action = ""
        self._remaining_sec = 0
        self._use_fahrenheit = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(1000)

        runs.step_progress.connect(self._on_step_progress)
        runs.remaining_seconds_changed.connect(self._on_remaining)
        runs.run_phase_changed.connect(self._on_run_phase)

        self._on_run_phase(runs.phase())
        self._on_tick()

    def _format_temp(self, celsius: float) -> str:
        if self._use_fahrenheit:
            return f"{celsius * 9.0 / 5.0 + 32.0:.1f} °F"
        return f"{celsius:.1f} °C"

    def _on_tick(self) -> None:
        a = self._hal.ambient_reading()
        if a.valid and a.timestamp is not None:
            self._env.setText(
                f"环境 {self._format_temp(a.temperature_celsius)}  湿度 {a.humidity_rh:.1f} %RH"
            )
        else:
            self._env.setText("环境数据不可用")
        act = self._current_action or "空闲"
        self._action.setText(f"当前动作：{act}")
        if self._runs.phase() == RunSessionPhase.RUNNING:
            m, s = divmod(self._remaining_sec, 60)
            self._eta.setText(f"剩余约 {m:02d}:{s:02d}")
        elif self._runs.phase() == RunSessionPhase.PAUSED:
            self._eta.setText("已暂停")
        else:
            self._eta.setText("整体剩余：—")

    def _on_step_progress(self, _i: int, _n: int, action_label: str) -> None:
        self._current_action = action_label

    def _on_remaining(self, sec: int) -> None:
        self._remaining_sec = sec

    def _on_run_phase(self, p: RunSessionPhase) -> None:
        if p in (
            RunSessionPhase.IDLE,
            RunSessionPhase.COMPLETED,
            RunSessionPhase.FAILED,
        ):
            if p == RunSessionPhase.IDLE:
                self._current_action = "空闲"
            elif p == RunSessionPhase.COMPLETED:
                self._current_action = "已完成"
            elif p == RunSessionPhase.FAILED:
                self._current_action = "失败/已中止"

    def export_snapshot_dict(self) -> dict:
        """Structured status-bar view for JSON export (schema: status-bar-state)."""
        return snapshot_status_bar_state(
            self._hal,
            self._runs.phase(),
            self._current_action,
            self._remaining_sec,
            self._use_fahrenheit,
        )
