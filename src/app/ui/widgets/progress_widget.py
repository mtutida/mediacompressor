
from PySide6.QtWidgets import QProgressBar

class ProgressWidget(QProgressBar):

    def __init__(self):
        super().__init__()
        self.setMinimum(0)
        self.setMaximum(100)

    def update_progress(self, value: float):
        self.setValue(int(value))
