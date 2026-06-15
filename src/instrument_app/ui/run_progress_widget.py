from __future__ import annotations

from PySide6.QtWidgets import QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget

from instrument_app.domain.run_coordinator import RunCoordinator
from instrument_app.domain.run_models import RunSessionPhase


class RunProgressWidget(QWidget):
    """FR-005 / FR-006: show current step index, label, and coarse progress; abort control."""

    def __init__(self, runs: RunCoordinator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._runs = runs
        self._total = 1
        self._index = 0
        self._label = ""

        v = QVBoxLayout(self)
        self._title = QLabel("运行进度", self)
        self._title.setStyleSheet("font-weight:600;")
        v.addWidget(self._title)
        self._step_line = QLabel("步骤：—", self)
        self._step_line.setWordWrap(True)
        v.addWidget(self._step_line)
        self._bar = QProgressBar(self)
        self._bar.setRange(0, 1)
        self._bar.setValue(0)
        v.addWidget(self._bar)
        self._abort = QPushButton("中止运行", self)
        self._abort.clicked.connect(self._on_abort)
        v.addWidget(self._abort)

        runs.step_progress.connect(self._on_step_progress)
        runs.run_phase_changed.connect(self._on_phase)
        runs.run_finished.connect(self._on_finished)
        self._refresh_abort_enabled()
        self._on_phase(runs.phase())

    def _on_step_progress(self, step_i: int, n_steps: int, action_label: str) -> None:
        self._index = step_i
        self._total = max(1, n_steps)
        self._label = action_label
        self._render()

    def _on_phase(self, phase: RunSessionPhase) -> None:
        self._refresh_abort_enabled()
        if phase in (
            RunSessionPhase.IDLE,
            RunSessionPhase.COMPLETED,
            RunSessionPhase.FAILED,
        ):
            self._reset_display(phase)

    def _on_finished(self, _phase: RunSessionPhase) -> None:
        self._refresh_abort_enabled()

    def _refresh_abort_enabled(self) -> None:
        self._abort.setEnabled(self._runs.phase() == RunSessionPhase.RUNNING)

    def _reset_display(self, phase: RunSessionPhase) -> None:
        if phase == RunSessionPhase.RUNNING:
            return
        self._step_line.setText(
            "步骤：—"
            if phase == RunSessionPhase.IDLE
            else ("已完成" if phase == RunSessionPhase.COMPLETED else "已中止/失败")
        )
        self._bar.setRange(0, 1)
        self._bar.setValue(0 if phase != RunSessionPhase.COMPLETED else 1)

    def _render(self) -> None:
        if self._runs.phase() != RunSessionPhase.RUNNING:
            return
        self._step_line.setText(
            f"步骤 {self._index + 1}/{self._total}：{self._label}"
        )
        self._bar.setRange(0, self._total)
        self._bar.setValue(self._index + 1)

    def _on_abort(self) -> None:
        self._runs.abort_run()
