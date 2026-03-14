from PySide6.QtWidgets import QFrame, QVBoxLayout
from app.ui.file_list import FileList


class FileListContainer(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("FileListContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.file_list = FileList()
        layout.addWidget(self.file_list)

        self.setStyleSheet("""
        QFrame#FileListContainer {
            background: #2b2b2b;
            border: 1px solid #3a3a3a;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        """)
        