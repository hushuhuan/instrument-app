"""Application-wide Qt style (Fusion + QSS). Plan: GUI path B — qt-material–class polish without extra deps."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication


def _default_qss_path() -> Path:
    return Path(__file__).resolve().parent / "styles" / "app.qss"


def apply_app_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    path = _default_qss_path()
    if path.is_file():
        app.setStyleSheet(path.read_text(encoding="utf-8"))
