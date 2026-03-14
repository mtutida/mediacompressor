
import os
from collections import OrderedDict

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QPainter, QPen, QPixmap
from PySide6.QtWidgets import QStyledItemDelegate, QStyle

from app.ui.ui_palette import UIPalette


class ThumbCache(OrderedDict):
    MAX_ITEMS = 256

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        elif len(self) >= self.MAX_ITEMS:
            self.popitem(last=False)
        super().__setitem__(key, value)


THUMB_CACHE = ThumbCache()


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

        close = QRect(rect.right() - 26,
                      rect.top() + (self.HEADER_HEIGHT - 20) // 2,
                      24, 20)

        settings = QRect(action_x - 34,
                         rect.top() + self.HEADER_HEIGHT + self.ROW_HEIGHT + 6,
                         22, 22)

        folder = QRect(action_x - 34,
                       rect.top() + self.HEADER_HEIGHT + 6,
                       22, 22)

        run = QRect(action_x + 10,
                    rect.top() + self.HEADER_HEIGHT + 10,
                    self.ACTION_WIDTH - 20,
                    18)

        progress = QRect(action_x + 10,
                         rect.bottom() - self.PROGRESS_HEIGHT - 5,
                         self.ACTION_WIDTH - 20,
                         self.PROGRESS_HEIGHT)

        return {
            "folder": folder,
            "settings": settings,
            "remove": close,
            "run": run,
            "progress": progress,
        }

    def draw_close(self, painter, rect):

        cx = rect.center().x()
        cy = rect.center().y()
        size = 6

        pen = QPen(Qt.white, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        painter.drawLine(cx - size, cy - size, cx + size, cy + size)
        painter.drawLine(cx + size, cy - size, cx - size, cy + size)

    def _normalize_status(self, status):
        text = str(status)
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
        thumb = getattr(job, "thumbnail", None)

        status_text, raw_status = self._normalize_status(status)
        status_color = UIPalette.STATUS_COLORS.get(raw_status, UIPalette.STATUS_READY)

        painter.fillRect(card_rect, UIPalette.CARD_BG)
        painter.setPen(UIPalette.CARD_BORDER)
        painter.drawRect(rect)

        thumb_rect = QRect(rect.left() + 1,
                           rect.top() + 1,
                           self.THUMB_WIDTH - 2,
                           rect.height() - 2)

        if thumb and os.path.exists(thumb):
            pix = THUMB_CACHE.get(thumb)
            if pix is None:
                pix = QPixmap()
                if pix.load(thumb):
                    THUMB_CACHE[thumb] = pix

            if pix and not pix.isNull():
                scaled = pix.scaled(thumb_rect.size(),
                                    Qt.KeepAspectRatioByExpanding,
                                    Qt.SmoothTransformation)
                painter.drawPixmap(thumb_rect, scaled)

        action_x = rect.right() - self.ACTION_WIDTH
        info_x = rect.left() + self.THUMB_WIDTH + 12
        info_width = action_x - info_x - 8

        painter.setPen(QPen(UIPalette.SEPARATOR, 1))
        painter.drawLine(action_x - 4, rect.top() + 6, action_x - 4, rect.bottom() - 6)

        header_rect = QRect(rect.left() + self.THUMB_WIDTH,
                            rect.top(),
                            rect.width() - self.THUMB_WIDTH,
                            self.HEADER_HEIGHT)

        painter.fillRect(header_rect, UIPalette.CARD_HEADER)

        metrics = painter.fontMetrics()

        painter.setPen(UIPalette.TEXT)
        name_rect = QRect(info_x, rect.top(), info_width, self.HEADER_HEIGHT)
        painter.drawText(name_rect,
                         Qt.AlignLeft | Qt.AlignVCenter,
                         metrics.elidedText(name, Qt.ElideRight, info_width))

        metadata = f"{codec} • {resolution} • {fps}fps • {duration} • {container}"

        meta_rect = QRect(info_x,
                          rect.top() + self.HEADER_HEIGHT + 4,
                          info_width,
                          self.ROW_HEIGHT)

        painter.setPen(UIPalette.META)
        painter.drawText(meta_rect, Qt.AlignLeft | Qt.AlignVCenter, metadata)

        run_rect = actions["run"]

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(UIPalette.PRIMARY, 1))
        painter.drawRoundedRect(run_rect, 3, 3)

        painter.setPen(Qt.white)
        painter.drawText(run_rect, Qt.AlignCenter, "▶  Comprimir")

        progress_rect = actions["progress"]

        painter.setPen(Qt.NoPen)
        painter.setBrush(UIPalette.PROGRESS_TRACK)
        painter.drawRect(progress_rect)

        progress = max(0, min(progress, 100))
        fill = int(progress_rect.width() * (progress / 100))

        if fill > 0:
            fill_rect = QRect(progress_rect.left(),
                              progress_rect.top(),
                              fill,
                              progress_rect.height())
            painter.setBrush(status_color)
            painter.drawRect(fill_rect)

        painter.setPen(Qt.white)
        display_text = status_text
        if raw_status in ("RUNNING", "PROCESSING"):
            display_text = f"{progress}%"

        painter.drawText(progress_rect, Qt.AlignCenter, display_text)

        if view and hasattr(view, "_hover_index") and view._hover_index and view._hover_index == index:
            painter.fillRect(card_rect, UIPalette.CARD_HOVER)

        if option.state & QStyle.State_Selected:
            painter.fillRect(card_rect, UIPalette.HOVER_PRIMARY)

        painter.restore()
