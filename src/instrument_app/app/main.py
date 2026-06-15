from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from instrument_app.app.application_context import ApplicationContext
from instrument_app.ui.app_theme import apply_app_theme
from instrument_app.ui.main_window import MainWindow


def main() -> int:
    argv = sys.argv
    app = QApplication(argv)
    apply_app_theme(app)
    app.setApplicationName("InstrumentApp")
    app.setOrganizationName("Lab")
    ctx = ApplicationContext(argv)
    win = MainWindow(ctx)
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
