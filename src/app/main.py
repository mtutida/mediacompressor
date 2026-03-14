# =========================================
# Bootstrap UI — FASE 14.3
# Inicialização mínima de QApplication
# Sem alterar Engine/Scheduler
# =========================================

import sys

from PySide6.QtWidgets import QApplication, QToolTip
from PySide6.QtGui import QFont

from app.application_context import ApplicationContext
from app.core.app_version import APP_NAME, APP_VERSION
from app.ui.app_shell import AppShell


def main():

    # Application Context
    ctx = ApplicationContext()
    ctx.logger.info(
        f"{APP_NAME} {APP_VERSION} starting (Python {sys.version.split()[0]})"
    )

    # Qt Application
    qt_app = QApplication(sys.argv)

    QToolTip.setFont(QFont("Segoe UI", 9))

    qt_app.setStyleSheet("""
    QToolTip {
        background-color: #2b2b2b;
        color: white;
        border: 1px solid #555;
        padding: 4px;
    }
    """)
    qt_app.setApplicationName(APP_NAME)

    # Main Window
    window = AppShell(ctx)
    ctx.logger.info("Window object created")

    window.resize(900, 600)
    window.show()

    # Windows TitleBar color
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            DWMWA_CAPTION_COLOR = 35
            hwnd = int(window.winId())
            color = ctypes.c_int(0x00D77800)

            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                wintypes.HWND(hwnd),
                ctypes.c_int(DWMWA_CAPTION_COLOR),
                ctypes.byref(color),
                ctypes.sizeof(color),
            )
        except Exception:
            pass

    # Run Qt loop
    exit_code = qt_app.exec()

    ctx.logger.info("Application shutdown")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
    