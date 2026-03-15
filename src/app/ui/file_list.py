
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QAbstractItemView, QListView, QStyleOptionViewItem

import os

from app.interaction_model.event_bridge import event_bridge
from app.ui.file_card_delegate import FileCardDelegate


VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".mkv", ".avi",
    ".webm", ".m4v", ".mpg", ".mpeg"
}


def collect_media_files(path):

    results = []

    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        if ext in VIDEO_EXTENSIONS:
            results.append(path)

    elif os.path.isdir(path):

        for root, _, files in os.walk(path):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in VIDEO_EXTENSIONS:
                    results.append(os.path.join(root, f))

    return results


class FileList(QListView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("FileList")
        self.setContentsMargins(0, 0, 0, 0)

        self.setUniformItemSizes(True)
        self.setLayoutMode(QListView.Batched)
        self.setBatchSize(20)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

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

        self.setDragDropMode(QAbstractItemView.DropOnly)

        self.viewport().installEventFilter(self)

        self.setStyleSheet(
            "QListView { background: transparent; border: none; }"
        )

    def eventFilter(self, obj, event):

        if obj is self.viewport():

            if event.type() == QEvent.DragEnter:
                self.dragEnterEvent(event)
                return True

            if event.type() == QEvent.DragMove:
                self.dragMoveEvent(event)
                return True

            if event.type() == QEvent.DragLeave:
                self.dragLeaveEvent(event)
                return True

            if event.type() == QEvent.Drop:
                self.dropEvent(event)
                return True

        return super().eventFilter(obj, event)

    def dragEnterEvent(self, event):

        if event.mimeData().hasUrls():
            self._drag_active = True
            self.viewport().update()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._drag_active = False
        self.viewport().update()
        event.accept()

    def dropEvent(self, event):

        self._drag_active = False
        self.viewport().update()

        if not event.mimeData().hasUrls():
            event.ignore()
            return

        paths = []

        for url in event.mimeData().urls():

            dropped_path = url.toLocalFile()

            if not dropped_path:
                continue

            paths.extend(collect_media_files(dropped_path))

        if paths:
            event_bridge.emit("files_dropped", {"paths": paths})

        event.acceptProposedAction()

    # -----------------------
    # Hover logic
    # -----------------------

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

            for action, rect in rects.items():

                if action == "progress":
                    continue

                if rect.contains(pos):
                    hovered_action = action
                    break

        if hovered_action:
            self.viewport().setCursor(Qt.PointingHandCursor)
        else:
            self.viewport().setCursor(Qt.ArrowCursor)

        self._hover_index = index if index.isValid() else None
        self._hover_action = hovered_action

        if prev_index != self._hover_index or prev_action != self._hover_action:

            if prev_index and prev_index.isValid():
                self.viewport().update(self.visualRect(prev_index))

            if self._hover_index and self._hover_index.isValid():
                self.viewport().update(self.visualRect(self._hover_index))

        super().mouseMoveEvent(event)

    def leaveEvent(self, event):

        if self._hover_index and self._hover_index.isValid():
            self.viewport().update(self.visualRect(self._hover_index))

        self._hover_index = None
        self._hover_action = None

        self.viewport().setCursor(Qt.ArrowCursor)

        super().leaveEvent(event)

    # -----------------------
    # Button click handling
    # -----------------------

    def mousePressEvent(self, event):

        pos = event.pos()
        index = self.indexAt(pos)

        if not index.isValid():
            return super().mousePressEvent(event)

        item_rect = self.visualRect(index)

        option = QStyleOptionViewItem()
        option.rect = item_rect

        rects = self.delegate.get_action_rects(option, index)

        job = index.data(self.delegate.ROLE_JOB)

        if job is None:
            return super().mousePressEvent(event)

        if rects["progress"].contains(pos):
            return

        if rects["run"].contains(pos):
            event_bridge.emit("job_run_requested", job)
            return

        if rects["settings"].contains(pos):
            event_bridge.emit("job_settings_requested", job)
            return

        if rects["remove"].contains(pos):
            event_bridge.emit("job_remove_requested", job)
            return

        if rects["folder"].contains(pos):
            event_bridge.emit("job_open_folder_requested", job)
            return

        action_column_start = item_rect.right() - self.delegate.ACTION_WIDTH

        if pos.x() >= action_column_start:
            return

        super().mousePressEvent(event)

