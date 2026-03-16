from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def _is_dark_theme():
    app = QApplication.instance()
    if not app:
        return True
    palette = app.palette()
    return palette.color(QPalette.Window).lightness() < 128


class UIPalette:

    if _is_dark_theme():
        # Dark Theme (current design)
        CARD_BG = QColor(43, 43, 43)
        CARD_BORDER = QColor(90, 90, 90)
        CARD_HEADER = QColor(53, 53, 53)

        TEXT = QColor(220, 220, 220)
        META = QColor(170, 170, 170)

        SEPARATOR = QColor(70, 70, 70)

        PRIMARY = QColor(90, 140, 220)
        PROGRESS_TRACK = QColor(20, 20, 20)

        CARD_HOVER = QColor(255, 255, 255, 20)
        HOVER_NEUTRAL = QColor(255, 255, 255, 30)
        HOVER_PRIMARY = QColor(70, 140, 255, 80)
        HOVER_DANGER = QColor(220, 40, 40, 120)

        PRESSED_PRIMARY = QColor(40, 110, 220, 120)

    else:
        # Light Theme
        CARD_BG = QColor(245, 245, 245)
        CARD_BORDER = QColor(200, 200, 200)
        CARD_HEADER = QColor(230, 230, 230)

        TEXT = QColor(40, 40, 40)
        META = QColor(90, 90, 90)

        SEPARATOR = QColor(210, 210, 210)

        PRIMARY = QColor(60, 120, 220)
        PROGRESS_TRACK = QColor(230, 230, 230)

        CARD_HOVER = QColor(0, 0, 0, 10)
        HOVER_NEUTRAL = QColor(0, 0, 0, 20)
        HOVER_PRIMARY = QColor(60, 120, 220, 80)
        HOVER_DANGER = QColor(220, 60, 60, 120)

        PRESSED_PRIMARY = QColor(60, 120, 220, 120)

    # Status colors (theme independent)
    STATUS_READY = QColor(150, 150, 150)
    STATUS_ANALYZING = QColor(70, 130, 220)
    STATUS_RUNNING = QColor(0, 180, 0)
    STATUS_DONE = QColor(0, 200, 120)
    STATUS_ERROR = QColor(200, 60, 60)

    STATUS_COLORS = {
        "READY": STATUS_READY,
        "ANALYZING": STATUS_ANALYZING,
        "PROCESSING": STATUS_RUNNING,
        "RUNNING": STATUS_RUNNING,
        "DONE": STATUS_DONE,
        "COMPLETED": STATUS_DONE,
        "ERROR": STATUS_ERROR,
        "FAILED": STATUS_ERROR,
    }
