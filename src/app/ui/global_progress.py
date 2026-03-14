
from PySide6.QtWidgets import QFrame, QHBoxLayout, QProgressBar

class GlobalProgressWidget(QFrame):

    def __init__(self,parent=None):
        super().__init__(parent)

        self.setObjectName("GlobalProgressWidget")
        self.setFixedHeight(24)

        layout=QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        self.progress=QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setMaximum(100)
        self.progress.setValue(0)

        layout.addWidget(self.progress)

        # The strip background is the frame itself
        self.setStyleSheet("""
        QFrame#GlobalProgressWidget{
            background:#3a3a3a;
        }

        QProgressBar{
            border:none;
            background:transparent;
        }

        QProgressBar::chunk{
            background:#3aa0ff;
        }
        """)

    def set_idle(self):
        self.progress.setValue(0)

    def set_progress(self,value,maximum):
        self.progress.setMaximum(maximum)
        self.progress.setValue(value)
