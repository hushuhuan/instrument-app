from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from instrument_app.app.application_context import ApplicationContext


class DeviceHealthDialog(QDialog):
    """FR-008: read-only device health summary from HAL."""

    def __init__(self, ctx: ApplicationContext, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("设备健康")
        self.setMinimumWidth(520)
        v = QVBoxLayout(self)
        rows = ctx.hal.device_health_summary()
        lines = []
        for name, ok, detail in rows:
            tag = "正常" if ok else "异常"
            lines.append(f"[{tag}] {name} — {detail}")
        body = QLabel("\n".join(lines), self)
        body.setWordWrap(True)
        body.setOpenExternalLinks(False)
        body.setStyleSheet("font-size: 13px;")
        v.addWidget(body)
        b = QPushButton("关闭", self)
        b.clicked.connect(self.accept)
        v.addWidget(b)
