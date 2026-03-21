from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QAbstractItemView, QListView, QStyleOptionViewItem

from app.interaction_model.event_bridge import event_bridge
from app.interaction_model.execution_controller import execution_controller
from app.ui.file_card_delegate import FileCardDelegate


class FileList(QListView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("FileList")

        self.setContentsMargins(0, 0, 0, 0)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setLayoutMode(QListView.Batched)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.delegate = FileCardDelegate(self)
        self.setItemDelegate(self.delegate)

        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)

        self._hover_index = None
        self._hover_action = None

        self._drag_active = False
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)

        self.setStyleSheet(
            "QListView { background: transparent; border: none; }"
            "QListView::viewport { background: transparent; }"
        )
        self.setSpacing(8)
        self.setViewportMargins(6, 6, 6, 6)

    # rest of class intentionally unchanged in patch context
