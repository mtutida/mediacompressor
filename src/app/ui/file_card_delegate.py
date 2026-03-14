
import os
from collections import OrderedDict

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QStyledItemDelegate, QStyle


class ThumbCache(OrderedDict):
    MAX_ITEMS = 256

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        elif len(self) >= self.MAX_ITEMS:
            self.popitem(last=False)
        super().__setitem__(key, value)


THUMB_CACHE = ThumbCache()

COLOR_BG = QColor(43, 43, 43)
COLOR_BORDER = QColor(90, 90, 90)
COLOR_HEADER = QColor(53, 53, 53)

COLOR_TEXT = QColor(220, 220, 220)
COLOR_META = QColor(170, 170, 170)

COLOR_SEPARATOR = QColor(70, 70, 70)

COLOR_ACTION_PRIMARY = QColor(90, 140, 220)
COLOR_PROGRESS_TRACK = QColor(20, 20, 20)

CARD_HOVER = QColor(255, 255, 255, 20)
CONTROL_HOVER_NEUTRAL = QColor(255, 255, 255, 30)
CONTROL_HOVER_PRIMARY = QColor(70, 140, 255, 80)
CONTROL_HOVER_DANGER = QColor(255, 80, 80, 70)

PRESSED_PRIMARY = QColor(40, 110, 220, 120)

STATUS_COLORS = {
    "READY": QColor(150, 150, 150),
    "ANALYZING": QColor(70, 130, 220),
    "PROCESSING": QColor(0, 180, 0),
    "RUNNING": QColor(0, 180, 0),
    "DONE": QColor(0, 200, 120),
    "COMPLETED": QColor(0, 200, 120),
    "ERROR": QColor(200, 60, 60),
    "FAILED": QColor(200, 60, 60),
}

STATUS_TEXT_MAP = {
    "READY": "PRONTO",
    "RUNNING": "PROCESSANDO",
    "PROCESSING": "PROCESSANDO",
    "COMPLETED": "CONCLUÍDO",
    "DONE": "CONCLUÍDO",
    "FAILED": "FALHA",
    "ERROR": "FALHA",
    "CANCELLED": "CANCELADO",
}


class FileCardDelegate(QStyledItemDelegate):

    ROLE_JOB = Qt.UserRole + 1

    THUMB_WIDTH = 160
    ACTION_WIDTH = 180

    HEADER_HEIGHT = 26
    ROW_HEIGHT = 24
    PROGRESS_HEIGHT = 16

    CARD_HEIGHT = 90

    def sizeHint(self, option, index):
        return QSize(0, self.CARD_HEIGHT)

    def get_action_rects(self, option, index):

        rect = option.rect.adjusted(6, 4, -6, -4)
        action_x = rect.right() - self.ACTION_WIDTH

        close = QRect(rect.right() - 28, rect.top() + 4, 20, 20)

        settings = QRect(
            action_x - 34,
            rect.top() + self.HEADER_HEIGHT + self.ROW_HEIGHT + 6,
            22,
            22,
        )

        folder = QRect(
            action_x - 34,
            rect.top() + self.HEADER_HEIGHT + 6,
            22,
            22,
        )

        run = QRect(
            action_x + 10,
            rect.top() + self.HEADER_HEIGHT + 10,
            self.ACTION_WIDTH - 20,
            18,
        )

        progress = QRect(
            action_x + 10,
            rect.bottom() - self.PROGRESS_HEIGHT - 5,
            self.ACTION_WIDTH - 20,
            self.PROGRESS_HEIGHT,
        )

        return {
            "folder": folder,
            "settings": settings,
            "remove": close,
            "run": run,
            "progress": progress,
        }

    def draw_close(self, painter, rect):

        painter.setPen(QPen(Qt.white, 1.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)

        cx = rect.center().x() + 2
        cy = rect.center().y()
        size = 5

        painter.drawLine(cx - size, cy - size, cx + size, cy + size)
        painter.drawLine(cx + size, cy - size, cx - size, cy + size)

    def _normalize_status(self, status):
        text = status

        if not isinstance(text, str):
            text = str(text)

        if "." in text:
            text = text.split(".")[-1]

        return STATUS_TEXT_MAP.get(text, text), text

    def paint(self, painter, option, index):

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        card_rect = option.rect
        rect = option.rect.adjusted(6, 4, -6, -4)

        actions = self.get_action_rects(option, index)

        job = index.data(self.ROLE_JOB)
        if not job:
            painter.restore()
            return

        view = option.widget

        name = getattr(job, "file_name", "unknown")
        status = getattr(job, "status", "READY")

        codec = getattr(job, "codec", "?")
        resolution = getattr(job, "resolution", "?")
        fps = getattr(job, "fps", "?")
        duration = getattr(job, "duration", "?")
        container = getattr(job, "container", "?")

        progress = getattr(job, "progress", 0)

        dest = getattr(job, "output_path", None) or getattr(job, "source_path", "")
        dest = os.path.normpath(dest)

        thumb = getattr(job, "thumbnail", None)

        status_text, raw_status = self._normalize_status(status)
        status_color = STATUS_COLORS.get(raw_status, QColor(120, 120, 120))

        painter.fillRect(card_rect, COLOR_BG)
        painter.setPen(COLOR_BORDER)
        painter.drawRect(rect)

        thumb_rect = QRect(
            rect.left() + 1,
            rect.top() + 1,
            self.THUMB_WIDTH - 2,
            rect.height() - 2,
        )

        if thumb and os.path.exists(thumb):

            pix = THUMB_CACHE.get(thumb)

            if pix is None:
                pix = QPixmap()
                if pix.load(thumb):
                    THUMB_CACHE[thumb] = pix

            if pix and not pix.isNull():

                scaled = pix.scaled(
                    thumb_rect.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation,
                )

                painter.drawPixmap(thumb_rect, scaled)

        action_x = rect.right() - self.ACTION_WIDTH

        info_x = rect.left() + self.THUMB_WIDTH + 12
        info_width = action_x - info_x - 8

        painter.setPen(QPen(COLOR_SEPARATOR, 1))

        painter.drawLine(
            action_x - 4,
            rect.top() + 6,
            action_x - 4,
            rect.bottom() - 6,
        )

        header_rect = QRect(
            rect.left() + self.THUMB_WIDTH,
            rect.top(),
            rect.width() - self.THUMB_WIDTH,
            self.HEADER_HEIGHT,
        )

        painter.fillRect(header_rect, COLOR_HEADER)

        painter.setPen(QPen(COLOR_SEPARATOR, 1))
        painter.drawRect(header_rect)

        metrics = painter.fontMetrics()

        painter.setPen(Qt.white)

        painter.drawText(
            QRect(info_x, rect.top(), info_width, self.HEADER_HEIGHT),
            Qt.AlignLeft | Qt.AlignVCenter,
            metrics.elidedText(name, Qt.ElideRight, info_width),
        )

        folder_rect = actions["folder"]

        path_rect = QRect(
            info_x,
            rect.top() + self.HEADER_HEIGHT + 4,
            folder_rect.left() - info_x - 8,
            self.ROW_HEIGHT,
        )

        painter.setPen(COLOR_TEXT)

        painter.drawText(
            path_rect,
            Qt.AlignLeft | Qt.AlignVCenter,
            metrics.elidedText(dest, Qt.ElideMiddle, path_rect.width())
        )

        metadata = f"{codec} • {resolution} • {fps}fps • {duration} • {container}"

        meta_rect = QRect(
            info_x,
            path_rect.bottom(),
            info_width,
            self.ROW_HEIGHT,
        )

        painter.setPen(COLOR_META)
        painter.drawText(meta_rect, Qt.AlignLeft | Qt.AlignVCenter, metadata)

        painter.setPen(Qt.white)

        original_font = painter.font()

        icon_font = painter.font()
        icon_font.setPointSize(icon_font.pointSize() + 2)
        painter.setFont(icon_font)

        painter.drawText(actions["folder"], Qt.AlignCenter, "📂")
        painter.drawText(actions["settings"], Qt.AlignCenter, "⚙")

        painter.setFont(original_font)

        self.draw_close(painter, actions["remove"])

        run_rect = actions["run"]

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(COLOR_ACTION_PRIMARY, 1))
        painter.drawRoundedRect(run_rect, 3, 3)

        painter.setPen(Qt.white)

        font = painter.font()
        font.setPointSize(font.pointSize() - 1)
        painter.setFont(font)

        painter.drawText(run_rect, Qt.AlignCenter, "▶  Comprimir")

        progress_rect = actions["progress"]

        painter.setPen(Qt.NoPen)
        painter.setBrush(COLOR_PROGRESS_TRACK)
        painter.drawRect(progress_rect)

        progress = max(0, min(progress, 100))
        fill = int(progress_rect.width() * (progress / 100))

        if fill > 0:

            fill_rect = QRect(
                progress_rect.left(),
                progress_rect.top(),
                fill,
                progress_rect.height(),
            )

            painter.setBrush(status_color)
            painter.drawRect(fill_rect)

        painter.setPen(Qt.white)

        display_text = status_text
        if raw_status in ("RUNNING", "PROCESSING"):
            display_text = f"{progress}%"

        painter.drawText(progress_rect, Qt.AlignCenter, display_text)

        painter.setPen(QPen(QColor(120,120,120), 2))
        painter.drawLine(progress_rect.left(), progress_rect.top()+2, progress_rect.left(), progress_rect.bottom())
        painter.drawLine(progress_rect.right(), progress_rect.top()+2, progress_rect.right(), progress_rect.bottom())

        painter.setPen(QPen(QColor(90,90,90), 1))
        painter.drawLine(
            progress_rect.left()+2,
            progress_rect.top()+1,
            progress_rect.right()-2,
            progress_rect.top()+1
        )

        if view:

            if hasattr(view, "_pressed_index") and view._pressed_index == index and view._pressed_action == "run":

                painter.setPen(Qt.NoPen)
                painter.setBrush(PRESSED_PRIMARY)
                painter.drawRoundedRect(run_rect.adjusted(-1, -1, 1, 1), 3, 3)

            elif hasattr(view, "_hover_index") and view._hover_index == index and view._hover_action:

                action = view._hover_action
                hover_rect = actions.get(action)

                if hover_rect:

                    painter.setPen(Qt.NoPen)

                    if action == "run":
                        painter.setBrush(CONTROL_HOVER_PRIMARY)
                    elif action == "remove":
                        painter.setBrush(CONTROL_HOVER_DANGER)
                    else:
                        painter.setBrush(CONTROL_HOVER_NEUTRAL)

                    painter.drawRoundedRect(hover_rect.adjusted(-2, -2, 2, 2), 4, 4)

        if view and hasattr(view, "_hover_index"):
            if view._hover_index == index:
                painter.fillRect(card_rect, CARD_HOVER)

        if option.state & QStyle.State_Selected:
            painter.fillRect(card_rect, QColor(70, 90, 120, 120))

        painter.restore()
