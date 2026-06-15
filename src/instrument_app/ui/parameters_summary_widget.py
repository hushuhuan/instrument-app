from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from instrument_app.domain.recipe_models import ProcessParameters


class ParametersSummaryWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        self._text = QLabel(self)
        self._text.setWordWrap(True)
        lay.addWidget(self._text)

    def set_parameters(self, p: ProcessParameters) -> None:
        self._text.setText(
            f"反应时间 {p.reaction_time_sec} s | 搅拌 {p.stir_speed_rpm} rpm | 温度 {p.reaction_temp_c:.1f} ℃\n"
            f"溶剂：{p.solvent} | 取样 {p.sample_count}\n"
            f"冲洗：{p.rinse_params} | 萃取：{p.extraction_params} | 过滤：{p.filtration_params}"
        )
