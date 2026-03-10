
# =========================================
# Bootstrap UI — FASE 14.3
# Inicialização mínima de QApplication
# Sem alterar Engine/Scheduler
# =========================================

import sys
from PySide6.QtWidgets import QApplication

from ui.app_shell import AppShell


def main():
    app = QApplication(sys.argv)
    window = AppShell()

    window.resize(900, 600)
    window.show()

    # Windows TitleBar blue
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
                ctypes.sizeof(color)
            )
        except Exception:
            pass

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
