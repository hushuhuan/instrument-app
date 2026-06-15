from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QWidget,
)

from instrument_app.domain.recipe_models import ProcessParameters


class ParametersForm(QWidget):
    parameters_edited = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        form = QFormLayout(self)
        self._reaction_time = QSpinBox(self)
        self._reaction_time.setRange(1, 86400)
        self._reaction_time.setSuffix(" s")
        form.addRow("反应时间", self._reaction_time)

        self._stir = QSpinBox(self)
        self._stir.setRange(0, 2000)
        self._stir.setSuffix(" rpm")
        form.addRow("搅拌速度", self._stir)

        self._temp = QDoubleSpinBox(self)
        self._temp.setRange(-40.0, 250.0)
        self._temp.setDecimals(1)
        self._temp.setSuffix(" ℃")
        form.addRow("反应温度", self._temp)

        self._rinse = QLineEdit(self)
        form.addRow("冲洗参数", self._rinse)

        self._solvent = QLineEdit(self)
        form.addRow("溶剂", self._solvent)

        self._extraction = QLineEdit(self)
        form.addRow("萃取参数", self._extraction)

        self._filtration = QLineEdit(self)
        form.addRow("过滤参数", self._filtration)

        self._sample = QSpinBox(self)
        self._sample.setRange(0, 100)
        form.addRow("取样数量", self._sample)

        self._reaction_time.valueChanged.connect(self._emit)
        self._stir.valueChanged.connect(self._emit)
        self._temp.valueChanged.connect(self._emit)
        self._rinse.textChanged.connect(self._emit)
        self._solvent.textChanged.connect(self._emit)
        self._extraction.textChanged.connect(self._emit)
        self._filtration.textChanged.connect(self._emit)
        self._sample.valueChanged.connect(self._emit)

        d = ProcessParameters()
        d.solvent = "水"
        self.set_parameters(d)

    def _emit(self, *_args: object) -> None:
        self.parameters_edited.emit()

    def parameters(self) -> ProcessParameters:
        return ProcessParameters(
            reaction_time_sec=self._reaction_time.value(),
            stir_speed_rpm=self._stir.value(),
            reaction_temp_c=self._temp.value(),
            rinse_params=self._rinse.text(),
            solvent=self._solvent.text(),
            extraction_params=self._extraction.text(),
            filtration_params=self._filtration.text(),
            sample_count=self._sample.value(),
        )

    def set_parameters(self, p: ProcessParameters) -> None:
        self._reaction_time.setValue(p.reaction_time_sec)
        self._stir.setValue(p.stir_speed_rpm)
        self._temp.setValue(p.reaction_temp_c)
        self._rinse.setText(p.rinse_params)
        self._solvent.setText(p.solvent)
        self._extraction.setText(p.extraction_params)
        self._filtration.setText(p.filtration_params)
        self._sample.setValue(p.sample_count)
