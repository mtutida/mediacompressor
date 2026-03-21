from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from app.ui.context_bar import SelectionActionBarWidget
from app.ui.file_list import FileList


class FileListContainer(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("FileListContainer")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(6, 6, 6, 8)
        outer_layout.setSpacing(0)

        self.inner_panel = QFrame(self)
        self.inner_panel.setObjectName("FileListInnerPanel")

        inner_layout = QVBoxLayout(self.inner_panel)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        self.title_bar = SelectionActionBarWidget()
        self.title_bar.setVisible(True)
        self.title_bar.btn_config.hide()
        self.title_bar.btn_enqueue.hide()
        self.title_bar.btn_clear_selection.setText("Limpar seleção")

        title_layout = self.title_bar.layout()
        title_layout.setContentsMargins(8, 2, 8, 2)
        title_layout.setSpacing(8)
        self.title_bar.btn_delete.setFixedWidth(100)
        self.title_bar.btn_clear_selection.setFixedWidth(126)
        self.title_bar.setMinimumHeight(28)
        self.title_bar.setMaximumHeight(28)

        title_label = QLabel("Lista de arquivos")
        title_label.setObjectName("FileListTitleLabel")
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        title_layout.insertWidget(0, title_label)
        title_layout.insertStretch(1, 1)

        self.file_list = FileList()
        self.file_list.setObjectName("InnerFileList")

        inner_layout.addWidget(self.title_bar)
        inner_layout.addWidget(self.file_list)
        outer_layout.addWidget(self.inner_panel)

        self.setStyleSheet(
            """
        QFrame#FileListContainer {
            background: palette(base);
            border: 2px solid palette(midlight);
            border-radius: 4px;
            padding: 1px;
        }

        QFrame#FileListInnerPanel {
            background: palette(alternate-base);
            border: none;
            border-radius: 3px;
        }

        QFrame#SelectionActionBarWidget {
            background: palette(alternate-base);
            border: none;
            border-radius: 3px 3px 0 0;
        }

        QListView#InnerFileList {
            background: transparent;
            border: none;
        }

        QFrame#SelectionActionBarWidget QPushButton {
            min-height: 22px;
            max-height: 22px;
        }

        QLabel#FileListTitleLabel {
            font-weight: 600;
            padding-left: 4px;
        }
        """
        )
