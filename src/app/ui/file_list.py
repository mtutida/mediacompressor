
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
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

        # Drag state
        self._drag_active = False
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)  # IMPORTANT FIX

        self.setStyleSheet(
            "QListView { background: transparent; border: none; }"
        )

    # ------------------------------------------------
    # Drag highlight
    # ------------------------------------------------

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
            path = url.toLocalFile()
            if path:
                paths.append(path)

        if paths:
            event_bridge.emit("files_dropped", {"paths": paths})

        event.acceptProposedAction()

    # ------------------------------------------------
    # EMPTY STATE (dropzone UI)
    # ------------------------------------------------

    def paintEvent(self, event):

        super().paintEvent(event)

        model = self.model()

        if not model or model.rowCount() != 0:
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.viewport().rect()
        center_y = rect.center().y()

        pen = QPen(QColor(90, 90, 90))
        pen.setStyle(Qt.DashLine)
        pen.setWidth(2)

        if self._drag_active:
            pen.setColor(QColor(120, 170, 255))

        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        drop_rect = rect.adjusted(40, 40, -40, -40)
        painter.drawRoundedRect(drop_rect, 8, 8)

        font = painter.font()
        font.setPointSize(34)
        painter.setFont(font)

        painter.setPen(QColor(120, 120, 120))

        painter.drawText(
            rect.adjusted(0, center_y - 120, 0, 0),
            Qt.AlignHCenter,
            "⬆"
        )

        font.setPointSize(20)
        font.setBold(True)
        painter.setFont(font)

        title = "Solte os arquivos para adicionar" if self._drag_active else "Arraste arquivos aqui"

        painter.drawText(
            rect.adjusted(0, center_y - 70, 0, 0),
            Qt.AlignHCenter,
            title
        )

        font.setPointSize(12)
        font.setBold(False)
        painter.setFont(font)

        painter.setPen(QColor(130, 130, 130))

        painter.drawText(
            rect.adjusted(0, center_y - 30, 0, 0),
            Qt.AlignHCenter,
            "ou use os botões acima"
        )

        painter.setPen(QColor(100, 100, 100))

        painter.drawText(
            rect.adjusted(0, center_y + 0, 0, 0),
            Qt.AlignHCenter,
            "Adicionar → escolher arquivos e configurar saída"
        )

        painter.drawText(
            rect.adjusted(0, center_y + 22, 0, 0),
            Qt.AlignHCenter,
            "Adicionar rápido → escolher arquivos e adicionar direto"
        )

        painter.drawText(
            rect.adjusted(0, center_y + 44, 0, 0),
            Qt.AlignHCenter,
            "Importar pasta → adicionar todos os arquivos da pasta"
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
