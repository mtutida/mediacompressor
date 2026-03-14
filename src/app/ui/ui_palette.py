
from PySide6.QtGui import QColor

class UIPalette:
    # Card
    CARD_BG = QColor(43, 43, 43)
    CARD_BORDER = QColor(90, 90, 90)
    CARD_HEADER = QColor(53, 53, 53)

    # Text
    TEXT = QColor(220, 220, 220)
    META = QColor(170, 170, 170)

    # Layout
    SEPARATOR = QColor(70, 70, 70)

    # Actions
    PRIMARY = QColor(90, 140, 220)
    PROGRESS_TRACK = QColor(20, 20, 20)

    # Hover / states
    CARD_HOVER = QColor(255, 255, 255, 20)
    HOVER_NEUTRAL = QColor(255, 255, 255, 30)
    HOVER_PRIMARY = QColor(70, 140, 255, 80)
    HOVER_DANGER = QColor(220, 40, 40, 120)

    PRESSED_PRIMARY = QColor(40, 110, 220, 120)

    # Status
    STATUS_READY = QColor(150,150,150)
    STATUS_ANALYZING = QColor(70,130,220)
    STATUS_RUNNING = QColor(0,180,0)
    STATUS_DONE = QColor(0,200,120)
    STATUS_ERROR = QColor(200,60,60)

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
