from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from instrument_app.domain.parameter_validation import validate_reaction_task_minimal
from instrument_app.domain.recipe_models import ProcessParameters


class ReactionTaskDialog(QDialog):
    def __init__(
        initial: ProcessParameters, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("反应任务")
        root = QVBoxLayout(self)
        form = QFormLayout()

        self._reaction_time = QSpinBox(self)
        self._reaction_time.setRange(1, 86400)
        self._reaction_time.setSuffix(" s")
        self._reaction_time.setValue(initial.reaction_time_sec)
        form.addRow("反应时间", self._reaction_time)

        self._temp = QDoubleSpinBox(self)
        self._temp.setRange(-40.0, 250.0)
        self._temp.setDecimals(1)
        self._temp.setSuffix(" ℃")
        self._temp.setValue(initial.reaction_temp_c)
        form.addRow("反应温度", self._temp)

        self._stir = QSpinBox(self)
        self._stir.setRange(0, 2000)
        self._stir.setSuffix(" rpm")
        self._stir.setValue(initial.stir_speed_rpm)
        form.addRow("搅拌速度（可选）", self._stir)

        root.addLayout(form)
        self._errors = QLabel(self)
        self._errors.setStyleSheet("color: #b00020;")
        self._errors.setWordWrap(True)
        root.addWidget(self._errors)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        root.addWidget(buttons)
        buttons.accepted.connect(self._try_accept)
        buttons.rejected.connect(self.reject)

    def _try_accept(self) -> None:
        p = self.result_parameters()
        err = validate_reaction_task_minimal(p)
        if err:
            self._errors.setText("\n".join(err))
            return
        self.accept()

    def result_parameters(self) -> ProcessParameters:
        return ProcessParameters(
            reaction_time_sec=self._reaction_time.value(),
            reaction_temp_c=self._temp.value(),
            stir_speed_rpm=self._stir.value(),
        )
