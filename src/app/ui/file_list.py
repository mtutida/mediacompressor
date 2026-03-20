from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
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

        self.setStyleSheet("QListView { background: transparent; border: none; }")
        self.setViewportMargins(0, 0, 6, 0)

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

        if not painter.isActive():
            return

        try:
            painter.setRenderHint(QPainter.Antialiasing)

            rect = self.viewport().rect()
            center_y = rect.center().y()

            palette = self.palette()

            secondary = palette.text().color()
            secondary.setAlpha(160)

            # -------------------------
            # Drop zone border
            # -------------------------

            # pen = QPen(palette.mid().color())

            border = palette.text().color()
            border.setAlpha(80)
            pen = QPen(border)

            pen.setStyle(Qt.DashLine)
            pen.setWidth(2)

            if self._drag_active:
                pen.setColor(palette.highlight().color())

            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            drop_rect = rect.adjusted(60, 60, -60, -60)
            painter.drawRoundedRect(drop_rect, 10, 10)

            # -------------------------
            # Icon
            # -------------------------

            font = painter.font()
            font.setPointSize(40)
            painter.setFont(font)

            painter.setPen(palette.text().color())

            painter.drawText(rect.adjusted(0, center_y - 140, 0, 0), Qt.AlignHCenter, "⬆")

            # -------------------------
            # Title
            # -------------------------

            font.setPointSize(22)
            font.setBold(True)
            painter.setFont(font)

            title = (
                "Solte os arquivos para adicionar"
                if self._drag_active
                else "Arraste arquivos aqui"
            )

            painter.drawText(rect.adjusted(0, center_y - 70, 0, 0), Qt.AlignHCenter, title)

            # -------------------------
            # Subtitle
            # -------------------------

            font.setPointSize(13)
            font.setBold(False)
            painter.setFont(font)

            painter.setPen(secondary)

            painter.drawText(
                rect.adjusted(0, center_y - 10, 0, 0),
                Qt.AlignHCenter,
                'ou clique em "Adicionar"',
            )

            # -------------------------
            # Separator
            # -------------------------

            sep_y = center_y - 20

            painter.setPen(QPen(secondary, 1))
            painter.drawLine(rect.center().x() - 140, sep_y, rect.center().x() + 140, sep_y)

            # -------------------------
            # Instructions
            # -------------------------

            font.setPointSize(11)
            painter.setFont(font)

            painter.setPen(secondary)

            painter.drawText(
                rect.adjusted(0, center_y + 30, 0, 0),
                Qt.AlignHCenter,
                "[ Adicionar ] → escolher arquivos e configurar saída",
            )

            painter.drawText(
                rect.adjusted(0, center_y + 55, 0, 0),
                Qt.AlignHCenter,
                "[ Adicionar rápido ] → adicionar arquivo direto na fila",
            )

            painter.drawText(
                rect.adjusted(0, center_y + 80, 0, 0),
                Qt.AlignHCenter,
                "[ Importar pasta ] → adicionar todos os arquivos da pasta",
            )

        finally:
            painter.end()



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
            status = getattr(job, "status", "READY")
            if status in ("RUNNING", "PROCESSING", "QUEUED"):
                event_bridge.emit("job_cancel_requested", job)
            else:
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

        already_selected = self.selectionModel().isSelected(index)

        super().mousePressEvent(event)

        if already_selected:
            from PySide6.QtCore import QItemSelectionModel

            self.selectionModel().select(index, QItemSelectionModel.Deselect)


    # ------------------------------------------------
    # Keyboard shortcuts
    # ------------------------------------------------

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Delete:

            indexes = self.selectedIndexes()
            if not indexes:
                return

            jobs = []
            for index in indexes:
                job = index.data(self.delegate.ROLE_JOB)
                if job:
                    jobs.append(job)

            if not jobs:
                return

            from PySide6.QtWidgets import QMessageBox, QCheckBox
            from app.ancillary.configuration import ConfigurationService

            cfg_service = ConfigurationService.instance()
            cfg = cfg_service.get()

            if cfg.confirm_delete:

                # collect job names for preview
                names = []
                for job in jobs:
                    name = getattr(job, "file_name", None)
                    if name:
                        names.append(name)

                preview = "\n".join(names[:3])
                if len(names) > 3:
                    preview += f"\n... e mais {len(names) - 3}"

                msg = QMessageBox(self)
                msg.setWindowTitle("Remover itens da fila")
                msg.setText(f"Remover {len(jobs)} item(ns) selecionado(s)?")
                if preview:
                    msg.setInformativeText(preview)

                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
                msg.setDefaultButton(QMessageBox.Cancel)

                checkbox = QCheckBox("Não mostrar novamente")
                msg.setCheckBox(checkbox)

                result = msg.exec()

                if checkbox.isChecked():
                    cfg_service.update(confirm_delete=False)

                if result != QMessageBox.Yes:
                    return

            seen = set()
            for job in jobs:
                if id(job) in seen:
                    continue
                seen.add(id(job))

                event_bridge.emit("job_remove_requested", job)

            return

        super().keyPressEvent(event)
