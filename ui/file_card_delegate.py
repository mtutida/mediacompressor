
import os
from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen

# simple thumbnail cache
THUMB_CACHE = {}

COLOR_BORDER = QColor(90, 90, 90)
COLOR_META = QColor(180, 180, 180)
COLOR_TEXT = QColor(200, 200, 200)
COLOR_BG = QColor(43, 43, 43)
COLOR_HOVER = QColor(60, 60, 60)
COLOR_SELECTED = QColor(70, 90, 120)


class FileCardDelegate(QStyledItemDelegate):

    ROLE_JOB = Qt.UserRole + 1

    PADDING = 10
    ROW_HEIGHT = 24
    ROW_SPACING = 4
    ACTION_HEIGHT = 34
    ACTION_SPACING = 6
    THUMB_WIDTH = 96

    HEADER_HEIGHT = ROW_HEIGHT + ROW_SPACING + ROW_HEIGHT + ROW_SPACING + ROW_HEIGHT
    CARD_HEIGHT = PADDING + HEADER_HEIGHT + ACTION_SPACING + ACTION_HEIGHT + PADDING

    def sizeHint(self, option, index):
        return QSize(0, self.CARD_HEIGHT)

    def draw_close(self, painter, rect):
        size = 20
        btn = QRect(rect.right() - size, rect.top() + 2, size, size)
        painter.setBrush(QColor(200, 50, 50))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(btn)

        painter.setPen(QPen(Qt.white, 2))
        cx = btn.center().x()
        cy = btn.center().y()
        painter.drawLine(cx-5, cy-5, cx+5, cy+5)
        painter.drawLine(cx+5, cy-5, cx-5, cy+5)

    def draw_badge(self, painter, rect, text):
        badge = QRect(rect.right()-90, rect.top()+2, 60, 18)
        painter.setBrush(QColor(120,120,120))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(badge, 9, 9)
        painter.setPen(Qt.white)
        painter.drawText(badge, Qt.AlignCenter, text)

    def paint(self, painter, option, index):

        painter.save()

        rect = option.rect.adjusted(6, 4, -6, -4)

        # background handling (delegate controls it fully)
        if option.state & QStyle.State_Selected:
            painter.fillRect(rect, COLOR_SELECTED)
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(rect, COLOR_HOVER)
        else:
            painter.fillRect(rect, COLOR_BG)

        painter.setPen(COLOR_BORDER)
        painter.drawRect(rect)

        job = index.data(self.ROLE_JOB)

        if job is None:
            painter.setPen(Qt.white)
            painter.drawText(rect, Qt.AlignLeft, str(index.data()))
            painter.restore()
            return

        name = getattr(job, "file_name", "unknown")
        status = getattr(job, "status", "READY")
        codec = getattr(job, "codec", "?")
        resolution = getattr(job, "resolution", "?")
        fps = getattr(job, "fps", "?")
        duration = getattr(job, "duration", "?")
        container = getattr(job, "container", "?")
        progress = getattr(job, "progress", 0)
        thumb = getattr(job, "thumbnail", None)
        dest = getattr(job, "output_path", None) or getattr(job, "source_path", "")

        thumb_rect = QRect(
            rect.left() + self.PADDING,
            rect.top() + self.PADDING,
            self.THUMB_WIDTH,
            self.HEADER_HEIGHT
        )

        if thumb and isinstance(thumb, str) and os.path.exists(thumb):
            pix = THUMB_CACHE.get(thumb)
            if pix is None:
                pix = QPixmap(thumb)
                if not pix.isNull():
                    THUMB_CACHE[thumb] = pix
            if pix and not pix.isNull():
                painter.drawPixmap(thumb_rect, pix)

        content_x = thumb_rect.right() + 12
        content_w = rect.right() - content_x - self.PADDING

        row1_y = rect.top() + self.PADDING
        row2_y = row1_y + self.ROW_HEIGHT + self.ROW_SPACING
        row3_y = row2_y + self.ROW_HEIGHT + self.ROW_SPACING
        action_y = rect.top() + self.PADDING + self.HEADER_HEIGHT + self.ACTION_SPACING

        filename_rect = QRect(content_x, row1_y, content_w-120, self.ROW_HEIGHT)

        painter.setPen(Qt.white)
        metrics = painter.fontMetrics()
        name = metrics.elidedText(name, Qt.ElideRight, filename_rect.width())
        painter.drawText(filename_rect, Qt.AlignLeft | Qt.AlignVCenter, name)

        self.draw_badge(painter, filename_rect, status)
        self.draw_close(painter, filename_rect)

        dest_rect = QRect(content_x, row2_y, content_w-30, self.ROW_HEIGHT)
        folder_rect = QRect(rect.right()-30, row2_y, 22, self.ROW_HEIGHT)

        painter.setPen(COLOR_TEXT)
        painter.drawText(dest_rect, Qt.AlignLeft | Qt.AlignVCenter, dest)
        painter.drawText(folder_rect, Qt.AlignCenter, "📂")

        metadata = f"{codec} | {resolution} | {fps}fps | {duration} | {container}"
        meta_rect = QRect(content_x, row3_y, content_w-30, self.ROW_HEIGHT)
        settings_rect = QRect(rect.right()-30, row3_y, 22, self.ROW_HEIGHT)

        painter.setPen(COLOR_META)
        painter.drawText(meta_rect, Qt.AlignLeft | Qt.AlignVCenter, metadata)
        painter.drawText(settings_rect, Qt.AlignCenter, "⚙")

        expand_rect = QRect(content_x, action_y, 32, self.ACTION_HEIGHT)
        run_rect = QRect(rect.right()-36, action_y, 34, self.ACTION_HEIGHT)
        progress_rect = QRect(
            expand_rect.right()+10,
            action_y+12,
            run_rect.left()-expand_rect.right()-20,
            8
        )

        painter.setPen(Qt.white)
        painter.drawText(expand_rect, Qt.AlignCenter, "▾")
        painter.drawText(run_rect, Qt.AlignCenter, "▶")

        if status == "PROCESSING":
            progress = max(0, min(progress, 100))
            painter.setPen(QColor(120,120,120))
            painter.drawRect(progress_rect)
            fill = int(progress_rect.width()*(progress/100))
            if fill > 0:
                painter.fillRect(
                    QRect(progress_rect.left(), progress_rect.top(), fill, progress_rect.height()),
                    QColor(0,180,0)
                )

        painter.restore()
