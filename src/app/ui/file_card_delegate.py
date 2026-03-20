import os
from collections import OrderedDict

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPalette, QPen, QPixmap
from PySide6.QtWidgets import QStyle, QStyledItemDelegate


def _parse_duration_to_seconds(d):
    try:
        if isinstance(d, (int, float)):
            return float(d)
        if isinstance(d, str) and ":" in d:
            parts = [float(p) for p in d.split(":")]
            if len(parts)==3:
                return parts[0]*3600 + parts[1]*60 + parts[2]
            if len(parts)==2:
                return parts[0]*60 + parts[1]
    except:
        pass
    return None


import subprocess, tempfile

_SAMPLE_CACHE = {}

def _smart_estimate(path, job, original_size):
    key = (path, getattr(job,"crf",None), getattr(job,"video_codec",None))
    if key in _SAMPLE_CACHE:
        return _SAMPLE_CACHE[key]

    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

        cmd = [
            "ffmpeg","-y",
            "-i", path,
            "-t","5",
            "-c:v", getattr(job,"video_codec","libx264"),
            "-crf", str(getattr(job,"crf",23)),
            "-preset", getattr(job,"preset","veryfast"),
            "-c:a", getattr(job,"audio_codec","aac"),
            tmp
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        sample_size = os.path.getsize(tmp)

        ratio_real = sample_size / original_size if original_size else 0

        if ratio_real > 0.9:
            est = original_size * 0.95
        else:
            duration_sec = _parse_duration_to_seconds(getattr(job,"duration",None))
            if duration_sec:
                est = sample_size * (duration_sec / 5.0)
                est = min(est, original_size * 1.1)
            else:
                est = original_size * 0.8

        _SAMPLE_CACHE[key] = est
        return est

    except:
        return None


class ThumbCache(OrderedDict):
    MAX_ITEMS = 256

    def __setitem__(self, key, value):
        if key in self:
            super().__delitem__(key)
        elif len(self) >= self.MAX_ITEMS:
            self.popitem(last=False)
        super().__setitem__(key, value)


THUMB_CACHE = ThumbCache()

CARD_HOVER = QColor(255, 255, 255, 20)
CONTROL_HOVER_NEUTRAL = QColor(255, 255, 255, 30)
CONTROL_HOVER_PRIMARY = QColor(70, 140, 255, 80)
CONTROL_HOVER_DANGER = QColor(200, 40, 40, 220)

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
    "QUEUED": "NA FILA",
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
    ACTION_WIDTH = 140

    HEADER_HEIGHT = 26
    ROW_HEIGHT = 24
    PROGRESS_HEIGHT = 16

    CARD_HEIGHT = 96

    def sizeHint(self, option, index):
        return QSize(0, self.CARD_HEIGHT)

    def get_action_rects(self, option, index):

        rect = option.rect.adjusted(8, 6, -8, -6)
        action_x = rect.right() - self.ACTION_WIDTH + 5 + 5

        close = QRect(
            option.rect.right() - 26,
            rect.top() + (self.HEADER_HEIGHT - 22) // 2,
            22,
            20,
        )

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

        run_width = self.ACTION_WIDTH - 24
        run_x = action_x + (self.ACTION_WIDTH - run_width) // 2

        run = QRect(
            run_x,
            rect.top() + self.HEADER_HEIGHT + 10,
            run_width,
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

        cx = rect.center().x()
        cy = rect.center().y()

        size = 6

        pen = QPen(Qt.white, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

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

        palette = option.palette

        card_rect = option.rect.adjusted(0, 3, 0, -3)
        rect = option.rect.adjusted(3, 4, -3, -6)

        actions = self.get_action_rects(option, index)

        job = index.data(self.ROLE_JOB)
        if not job:
            painter.restore()
            return

        view = option.widget

        source = getattr(job, "input_path", None) or getattr(job, "source_path", None)
        output_path = getattr(job, "output_path", None)

        name = getattr(job, "file_name", "unknown")

        try:
            if source and output_path:
                src_base = os.path.basename(source)
                src_name, src_ext = os.path.splitext(src_base)

                out_base = os.path.basename(output_path)
                out_name, out_ext = os.path.splitext(out_base)

                if src_ext == out_ext and out_name.startswith(src_name):
                    suffix = out_name[len(src_name) :]
                    if suffix:
                        name = f"{src_name} [{suffix}] {src_ext}"
                    else:
                        name = out_base
                else:
                    name = out_base
        except Exception:
            pass

        status = getattr(job, "status", "READY")

        codec = getattr(job, "codec", "?")
        resolution = getattr(job, "resolution", "?")
        fps = getattr(job, "fps", "?")
        duration = getattr(job, "duration", "?")
        container = getattr(job, "container", "?")
        source_size = getattr(job,"source_size",None)
        estimated_size = getattr(job,"estimated_size",None)

        progress = getattr(job, "progress", 0)

        dest_path = getattr(job, "output_path", None) or getattr(job, "source_path", "")
        dest = os.path.dirname(os.path.normpath(dest_path))

        thumb = getattr(job, "thumbnail", None)

        status_text, raw_status = self._normalize_status(status)
        status_color = STATUS_COLORS.get(raw_status, QColor(120, 120, 120))

        painter.fillRect(card_rect, palette.base())
        border = QColor(70, 140, 255)
        border.setAlpha(145)
        painter.setPen(QPen(border, 1.2))
        painter.drawRect(card_rect.adjusted(0, 0, -1, -1))

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

        action_x = rect.right() - self.ACTION_WIDTH + 5

        info_x = rect.left() + self.THUMB_WIDTH + 12
        info_width = action_x - info_x - 8

        painter.setPen(
            QPen((lambda c: (c.setAlpha(140), c)[1])(palette.text().color()), 1)
        )

        painter.drawLine(
            action_x - 4,
            rect.top() + self.HEADER_HEIGHT + 2,
            action_x - 4,
            rect.bottom() - 6,
        )

        header_rect = QRect(
            rect.left() + self.THUMB_WIDTH,
            rect.top(),
            rect.width() - self.THUMB_WIDTH,
            self.HEADER_HEIGHT,
        )

        header_color = palette.alternateBase().color()
        base_color = palette.base().color()

        if abs(header_color.lightness() - base_color.lightness()) < 10:
            if base_color.lightness() > 128:
                header_color = palette.midlight().color()
            else:
                header_color = palette.mid().color()

        if header_color.lightness() > 128:
            header_color = header_color.darker(78)
        else:
            header_color = header_color.lighter(104)

        painter.fillRect(header_rect, header_color)

        painter.setPen(
            QPen((lambda c: (c.setAlpha(140), c)[1])(palette.text().color()), 1)
        )
        # header border removed for cleaner look

        metrics = painter.fontMetrics()

        painter.setPen(palette.text().color())

        # --- render file size (computed from source_path) ---
        size_text = None

        if source and os.path.exists(source):
            try:
                # size_bytes = os.path.getsize(source)

                size_bytes = os.path.getsize(source)

                size = float(size_bytes)
                for unit in ["B","KB","MB","GB","TB"]:
                    if size < 1024:
                        original = f"{size:.1f} {unit}"
                        break
                    size /= 1024


                # original = f"{size_bytes / (1024*1024):.1f} MB"
                # print("DEBUG PATH:", source)
                # print("DEBUG SIZE_BYTES:", size_bytes)
                # print("DEBUG original:", original)
                # print("DEBUG size:", size)
                

                # estimation
                est_bytes = getattr(job, "estimated_size_bytes", None)
                if est_bytes is None:
                    est_bytes = size_bytes * 0.8
                est_bytes = min(est_bytes, size_bytes * 0.95)

                est = float(est_bytes)
                for unit in ["B","KB","MB","GB","TB"]:
                    if est < 1024:
                        estimated = f"{est:.1f} {unit}"
                        break
                    est /= 1024

                size_text = f"{original} → ≈{estimated}"

            except Exception:
                pass


            # except Exception:
            #     pass

        original_font = painter.font()
        font_bold = painter.font()
        font_bold.setBold(True)
        painter.setFont(font_bold)

        metrics = painter.fontMetrics()
        size_text_width = metrics.horizontalAdvance(size_text) + 10 if size_text else 0
        size_gap = 10 if size_text else 0
        size_rect = QRect(
            action_x - 4 - size_text_width,
            rect.top(),
            size_text_width,
            self.HEADER_HEIGHT,
        )
        name_right = size_rect.left() - size_gap if size_text else action_x - 14
        name_rect = QRect(info_x, rect.top(), max(40, name_right - info_x), self.HEADER_HEIGHT)

        # detect LAST suffix pattern like:  [_something] .ext
        suffix_start = name.rfind("[_")
        suffix_end = name.rfind("]")

        if suffix_start != -1 and suffix_end != -1 and suffix_end > suffix_start:
            base = name[:suffix_start]
            suffix = name[suffix_start : suffix_end + 1]
            ext = name[suffix_end + 1 :]
            full_width = (
                metrics.horizontalAdvance(base)
                + metrics.horizontalAdvance(suffix)
                + metrics.horizontalAdvance(ext)
            )

            if full_width <= name_rect.width():
                x = name_rect.left()

                painter.setPen(palette.text().color())
                painter.drawText(
                    QRect(x, name_rect.top(), name_rect.width(), self.HEADER_HEIGHT),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    base,
                )

                x += metrics.horizontalAdvance(base)

                painter.setPen(QColor(90, 140, 220))
                painter.drawText(
                    QRect(x, name_rect.top(), max(0, name_rect.right() - x), self.HEADER_HEIGHT),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    suffix,
                )

                x += metrics.horizontalAdvance(suffix)

                painter.setPen(palette.text().color())
                painter.drawText(
                    QRect(x, name_rect.top(), max(0, name_rect.right() - x), self.HEADER_HEIGHT),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    ext,
                )
            else:
                painter.setPen(palette.text().color())
                painter.drawText(
                    name_rect,
                    Qt.AlignLeft | Qt.AlignVCenter,
                    metrics.elidedText(name, Qt.ElideRight, name_rect.width()),
                )
        else:
            painter.setPen(palette.text().color())
            painter.drawText(
                name_rect,
                Qt.AlignLeft | Qt.AlignVCenter,
                metrics.elidedText(name, Qt.ElideRight, name_rect.width()),
            )

        if size_text:
            painter.setPen(palette.text().color())
            painter.drawText(size_rect, Qt.AlignRight | Qt.AlignVCenter, size_text)

        painter.setFont(original_font)

        folder_rect = actions["folder"]

        path_rect = QRect(
            info_x,
            rect.top() + self.HEADER_HEIGHT + 4,
            folder_rect.left() - info_x - 8,
            self.ROW_HEIGHT,
        )

        
        font_normal = painter.font()
        font_bold = painter.font()
        font_bold.setBold(True)

        label = "Pasta de destino:"
        value = " " + dest

        fm = painter.fontMetrics()
        x = path_rect.left()

        painter.setFont(font_bold)
        painter.setPen(palette.text().color())
        painter.drawText(
            QRect(x, path_rect.top(), path_rect.width(), path_rect.height()),
            Qt.AlignLeft | Qt.AlignVCenter,
            label,
        )
        x += fm.horizontalAdvance(label) + 4

        painter.setFont(font_normal)
        painter.drawText(
            QRect(x, path_rect.top(), path_rect.width(), path_rect.height()),
            Qt.AlignLeft | Qt.AlignVCenter,
            metrics.elidedText(value, Qt.ElideMiddle, path_rect.width()),
        )


        metadata = f"Resolução: {resolution} • FPS: {fps} • Duração: {duration}"

        meta_rect = QRect(
            info_x,
            path_rect.bottom(),
            info_width,
            self.ROW_HEIGHT,
        )

        meta = palette.text().color()
        meta.setAlpha(160)
        painter.setPen(meta)
        
        fm = painter.fontMetrics()
        
        font_normal = painter.font()
        font_bold = painter.font()
        font_bold.setBold(True)

        fm = painter.fontMetrics()
        x = meta_rect.left()
        parts = metadata.split(" • ")

        for i, part in enumerate(parts):
            if ":" in part:
                label, value = part.split(":", 1)
                label = label + ":"

                painter.setFont(font_bold)
                painter.setPen(palette.text().color())
                painter.drawText(
                    QRect(x, meta_rect.top(), meta_rect.width(), meta_rect.height()),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    label,
                )
                x += fm.horizontalAdvance(label) + 4

                painter.setFont(font_normal)
                value = value.strip()
                painter.drawText(
                    QRect(x, meta_rect.top(), meta_rect.width(), meta_rect.height()),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    value,
                )
                x += fm.horizontalAdvance(value)
            else:
                painter.setFont(font_normal)
                painter.drawText(
                    QRect(x, meta_rect.top(), meta_rect.width(), meta_rect.height()),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    part,
                )
                x += fm.horizontalAdvance(part)

            if i < len(parts) - 1:
                sep = " • "
                painter.setFont(font_normal)
                painter.drawText(
                    QRect(x, meta_rect.top(), meta_rect.width(), meta_rect.height()),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    sep,
                )
                x += fm.horizontalAdvance(sep)



        painter.setPen(palette.text().color())

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
        painter.setPen(QPen(palette.highlight().color(), 1))
        painter.drawRoundedRect(run_rect, 3, 3)

        painter.setPen(palette.text().color())

        font = painter.font()
        font.setPointSize(font.pointSize() - 1)
        painter.setFont(font)

        run_label = "▶  Comprimir"

        if raw_status in ("RUNNING", "PROCESSING", "QUEUED"):
            run_label = "■  Cancelar"

        painter.drawText(run_rect, Qt.AlignCenter, run_label)

        progress_rect = actions["progress"]

        painter.setPen(Qt.NoPen)
        base_lightness = palette.base().color().lightness()

        if base_lightness > 128:
            # light theme → darker gray
            track = palette.mid().color()
            track.setAlpha(140)
        else:
            # dark theme → lighter gray
            track = palette.midlight().color()
            track.setAlpha(120)

        painter.setBrush(track)
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

        # adaptive text color for progress bar
        base_lightness = palette.base().color().lightness()
        if base_lightness > 128:
            painter.setPen(palette.text().color())
        else:
            painter.setPen(palette.text().color())

        display_text = status_text
        if raw_status in ("RUNNING", "PROCESSING"):
            display_text = f"{progress}%"

        painter.drawText(progress_rect, Qt.AlignCenter, display_text)

        painter.setPen(QPen(palette.text().color(), 2))
        painter.drawLine(
            progress_rect.left(),
            progress_rect.top() + 2,
            progress_rect.left(),
            progress_rect.bottom(),
        )
        painter.drawLine(
            progress_rect.right(),
            progress_rect.top() + 2,
            progress_rect.right(),
            progress_rect.bottom(),
        )

        painter.setPen(
            QPen((lambda c: (c.setAlpha(140), c)[1])(palette.text().color()), 1)
        )
        painter.drawLine(
            progress_rect.left() + 2,
            progress_rect.top() + 1,
            progress_rect.right() - 2,
            progress_rect.top() + 1,
        )

        if view:

            if (
                hasattr(view, "_pressed_index")
                and view._pressed_index == index
                and view._pressed_action == "run"
            ):

                painter.setPen(Qt.NoPen)
                c=palette.highlight().color(); c.setAlpha(160); painter.setBrush(c)
                painter.drawRoundedRect(run_rect.adjusted(-1, -1, 1, 1), 3, 3)

            elif (
                hasattr(view, "_hover_index")
                and view._hover_index == index
                and view._hover_action
            ):

                action = view._hover_action
                hover_rect = actions.get(action)

                if hover_rect:

                    painter.setPen(Qt.NoPen)

                    if action == "run":
                        c=palette.highlight().color(); c.setAlpha(120); painter.setBrush(c)
                    elif action == "remove":
                        painter.setBrush(CONTROL_HOVER_DANGER)
                    else:
                        c=palette.midlight().color(); c.setAlpha(110); painter.setBrush(c)

                    painter.drawRoundedRect(hover_rect.adjusted(-4, -3, 2, 1), 4, 4)

                    if action == "remove":
                        self.draw_close(painter, hover_rect)

        
        if (
            view
            and hasattr(view, "_hover_index")
            and view._hover_index == index
            and not getattr(view, "_hover_action", None)
            and not getattr(view, "_pressed_action", None)
        ):

            base = palette.base().color()

            if base.lightness() > 128:
                hover = palette.mid().color()
                hover.setAlpha(110)
            else:
                hover = palette.midlight().color()
                hover.setAlpha(90)

            painter.fillRect(card_rect, hover)

            border = palette.highlight().color()
            border.setAlpha(110)
            painter.setPen(QPen(border, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(card_rect.adjusted(0, 0, -1, -1))


        if option.state & QStyle.State_Selected:
            painter.fillRect(card_rect, QColor(70, 90, 120, 120))

        painter.restore()
