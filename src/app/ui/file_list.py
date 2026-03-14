from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QListView, QStyleOptionViewItem

from app.interaction_model.event_bridge import event_bridge
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

        # Hover tracking
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)

        self._hover_index = None
        self._hover_action = None

        self.setStyleSheet(
            """
            QListView {
                background: transparent;
                border: none;
            }
            """
        )

    # ------------------------------------------------
    # Hover detection
    # ------------------------------------------------

    def mouseMoveEvent(self, event):

        pos = event.pos()
        index = self.indexAt(pos)

        prev_index = self._hover_index
        prev_action = self._hover_action

        hovered_action = None

        if index.isValid():

            item_rect = self.visualRect(index)

            option = QStyleOptionViewItem()
            option.rect = item_rect

            rects = self.delegate.get_action_rects(option, index)

            # converter posição do mouse para coordenada do item
            item_pos = pos - item_rect.topLeft()

            for action, rect in rects.items():
                if rect.contains(item_pos):
                    hovered_action = action
                    break

        if hovered_action:
            self.viewport().setCursor(Qt.PointingHandCursor)
        else:
            self.viewport().setCursor(Qt.ArrowCursor)

        self._hover_index = index if index.isValid() else None
        self._hover_action = hovered_action

        # repaint mínimo
        if prev_index != self._hover_index or prev_action != self._hover_action:

            if prev_index and prev_index.isValid():
                self.viewport().update(self.visualRect(prev_index))

            if self._hover_index and self._hover_index.isValid():
                self.viewport().update(self.visualRect(self._hover_index))

        super().mouseMoveEvent(event)

    # ------------------------------------------------
    # Clear hover
    # ------------------------------------------------

    def leaveEvent(self, event):

        if self._hover_index and self._hover_index.isValid():
            self.viewport().update(self.visualRect(self._hover_index))

        self._hover_index = None
        self._hover_action = None

        self.viewport().setCursor(Qt.ArrowCursor)

        super().leaveEvent(event)

    # ------------------------------------------------
    # Click handling
    # ------------------------------------------------

    def mousePressEvent(self, event):

        pos = event.pos()
        index = self.indexAt(pos)

        if not index.isValid():
            return super().mousePressEvent(event)

        item_rect = self.visualRect(index)

        option = QStyleOptionViewItem()
        option.rect = item_rect

        rects = self.delegate.get_action_rects(option, index)

        item_pos = pos - item_rect.topLeft()

        job = index.data(self.delegate.ROLE_JOB)

        if job is None:
            return super().mousePressEvent(event)

        if "run" in rects and rects["run"].contains(item_pos):
            event_bridge.emit("job_run_requested", job)
            return

        if "settings" in rects and rects["settings"].contains(item_pos):
            event_bridge.emit("job_settings_requested", job)
            return

        if "remove" in rects and rects["remove"].contains(item_pos):
            event_bridge.emit("job_remove_requested", job)
            return

        if "folder" in rects and rects["folder"].contains(item_pos):
            event_bridge.emit("job_open_folder_requested", job)
            return

        super().mousePressEvent(event)