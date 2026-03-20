from PySide6.QtWidgets import QFrame, QVBoxLayout

from app.ui.context_bar import SelectionActionBarWidget
from app.ui.file_list import FileList


class FileListContainer(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("FileListContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)

        self.inner_panel = QFrame()
        self.inner_panel.setObjectName("FileListInnerPanel")

        inner_layout = QVBoxLayout(self.inner_panel)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        self.title_bar = SelectionActionBarWidget()
        self.file_list = FileList()
        self.file_list.setObjectName("InnerFileList")

        inner_layout.addWidget(self.title_bar)
        inner_layout.addWidget(self.file_list)

        layout.addWidget(self.inner_panel)

        self.setStyleSheet(
            """
        QFrame#FileListContainer {
            border: 2px solid palette(midlight);
            border-radius: 4px;
            padding: 1px;
            background: palette(base);
        }

        QFrame#FileListInnerPanel {
            background: #e9e9e9;
            border: none;
            border-radius: 3px;
        }

        QFrame#SelectionActionBarWidget {
            background: #e8f1fb;
            border: none;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
            padding: 0px;
        }

        QListView#InnerFileList {
            background: #e9e9e9;
            border: none;
            border-bottom-left-radius: 3px;
            border-bottom-right-radius: 3px;
        }
        """
        )
