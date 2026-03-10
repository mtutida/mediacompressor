
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListView, QAbstractItemView
from ui.file_card_delegate import FileCardDelegate


class FileList(QListView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("FileList")

        self.setContentsMargins(0, 0, 0, 0)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setUniformItemSizes(True)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # IMPORTANT: enable hover tracking on the viewport
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.viewport().setAttribute(Qt.WA_Hover)

        self.setItemDelegate(FileCardDelegate(self))

        self.setStyleSheet("""
        QListView{
            background:transparent;
            border:none;
        }
        """)
