
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect


class ToastManager:

    def __init__(self, parent):

        self.parent = parent

        self.label = QLabel(parent)
        self.label.hide()

        self.label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.label.setStyleSheet(
            """
            QLabel {
                background: rgba(30,30,30,220);
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            """
        )

        self.label.setAlignment(Qt.AlignCenter)

        # opacity effect
        self.opacity = QGraphicsOpacityEffect()
        self.label.setGraphicsEffect(self.opacity)

        # animations
        self.fade_in = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_in.setDuration(150)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)

        self.fade_out = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_out.setDuration(200)
        self.fade_out.setStartValue(1)
        self.fade_out.setEndValue(0)

        self.slide = QPropertyAnimation(self.label, b"pos")
        self.slide.setDuration(180)
        self.slide.setEasingCurve(QEasingCurve.OutCubic)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._start_hide)

        self.fade_out.finished.connect(self.label.hide)

    # ------------------------------------------------

    def show(self, text, duration=2000):

        self.label.setText(text)
        self.label.adjustSize()

        parent_rect = self.parent.rect()

        x = (parent_rect.width() - self.label.width()) // 2
        y = parent_rect.height() // 2 - self.label.height()

        start_pos = QPoint(x, y + 15)
        end_pos = QPoint(x, y)

        self.label.move(start_pos)

        self.slide.stop()
        self.fade_in.stop()
        self.fade_out.stop()

        self.slide.setStartValue(start_pos)
        self.slide.setEndValue(end_pos)

        self.opacity.setOpacity(0)

        self.label.show()
        self.label.raise_()

        self.slide.start()
        self.fade_in.start()

        self.timer.start(duration)

    # ------------------------------------------------

    def _start_hide(self):

        self.fade_out.start()
