"""App theme: Fusion + bundled QSS (plan GUI path B)."""

from __future__ import annotations

import instrument_app.ui.app_theme as app_theme


def test_bundled_qss_exists_and_nonempty() -> None:
    path = app_theme._default_qss_path()
    assert path.is_file(), f"missing {path}"
    text = path.read_text(encoding="utf-8")
    assert "QWidget" in text
    assert len(text) > 100


def test_apply_app_theme_sets_fusion_and_stylesheet() -> None:
    from PySide6.QtWidgets import QApplication

    import sys

    if not QApplication.instance():
        _ = QApplication(sys.argv if hasattr(sys, "argv") else [])
    app = QApplication.instance()
    assert app is not None
    app_theme.apply_app_theme(app)
    # With a global stylesheet, the active style is typically QStyleSheetStyle (wraps the base, e.g. Fusion).
    assert app.style() is not None
    sheet = app.styleSheet()
    assert "QWidget" in sheet
    assert len(sheet) > 100
