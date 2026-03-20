from PySide6.QtWidgets import QFrame, QVBoxLayout

from app.ui.file_list import FileList


class FileListContainer(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("FileListContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 2, 8)
        layout.setSpacing(0)

        self.file_list = FileList()
        layout.addWidget(self.file_list)

        self.setStyleSheet(
            """
        QFrame#FileListContainer {

            border:2px solid palette(midlight);
            border-radius:4px;
            padding:1px;
        }
        """
        )
