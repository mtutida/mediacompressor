from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QTimer
import os

from app.interaction_model.event_bridge import event_bridge


class FileListModel(QAbstractListModel):

    ROLE_JOB = Qt.UserRole + 1
    ROLE_FILE_NAME = Qt.UserRole + 2
    ROLE_STATUS = Qt.UserRole + 3
    ROLE_PROGRESS = Qt.UserRole + 4
    ROLE_CODEC = Qt.UserRole + 5
    ROLE_RESOLUTION = Qt.UserRole + 6

    def __init__(self, interaction_model=None):
        super().__init__()

        self._items = []
        self._interaction_model = interaction_model

        # normalized path -> row
        self._job_row_map = {}

        # duplicate aggregation
        self._duplicate_counter = 0
        self._duplicate_timer = QTimer()
        self._duplicate_timer.setSingleShot(True)
        self._duplicate_timer.timeout.connect(self._emit_duplicate_feedback)

        event_bridge.subscribe(self._on_event)

    # ------------------------------------------------
    # Utils
    # ------------------------------------------------

    def _normalize_path(self, path):

        if not path:
            return None

        path = os.path.normpath(path)
        path = path.lower()

        return path

    def _rebuild_row_map(self):

        self._job_row_map.clear()

        for row, job in enumerate(self._items):

            key = self._normalize_path(getattr(job, "source_path", None))

            if key:
                self._job_row_map[key] = row

    def _emit_duplicate_feedback(self):

        if self._duplicate_counter == 0:
            return

        event_bridge.emit(
            "duplicate_files_ignored",
            {"count": self._duplicate_counter},
        )

        self._duplicate_counter = 0

    def _register_duplicate(self):

        self._duplicate_counter += 1

        # restart small timer to aggregate multiple duplicates
        self._duplicate_timer.start(120)

    # ------------------------------------------------
    # Model API
    # ------------------------------------------------

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def data(self, index, role):

        if not index.isValid():
            return None

        item = self._items[index.row()]

        if role == Qt.DisplayRole:
            return getattr(item, "file_name", "unknown")

        if role == Qt.ToolTipRole:

            dest = getattr(item, "output_path", None) or getattr(item, "source_path", "")

            if len(dest) > 60:
                return dest

            return None

        if role == self.ROLE_JOB:
            return item

        if role == self.ROLE_FILE_NAME:
            return getattr(item, "file_name", "unknown")

        if role == self.ROLE_STATUS:
            return getattr(item, "status", "pending")

        if role == self.ROLE_PROGRESS:
            return getattr(item, "progress", 0)

        if role == self.ROLE_CODEC:
            return getattr(item, "codec", "?")

        if role == self.ROLE_RESOLUTION:
            return getattr(item, "resolution", "?")

        return None

    def roleNames(self):
        return {
            self.ROLE_JOB: b"job",
            self.ROLE_FILE_NAME: b"file_name",
            self.ROLE_STATUS: b"status",
            self.ROLE_PROGRESS: b"progress",
            self.ROLE_CODEC: b"codec",
            self.ROLE_RESOLUTION: b"resolution",
        }

    # ------------------------------------------------
    # Event bridge
    # ------------------------------------------------

    def _on_event(self, event_type, payload):

        # ------------------------------------------------
        # JOB ENQUEUED
        # ------------------------------------------------

        if event_type == "job_enqueued":

            job = payload.get("job")
            if not job:
                return

            key = self._normalize_path(getattr(job, "source_path", None))

            # duplicate detection
            if key and key in self._job_row_map:
                self._register_duplicate()
                return

            
            # ------------------------------------------------
            # BUILD OUTPUT PATH
            # ------------------------------------------------
            try:
                from app.core.output_naming import generate_output_path

                source = getattr(job, "source_path", None)

                if source:
                    job.output_path = generate_output_path(source)

            except Exception:
                pass

            row = len(self._items)

            self.beginInsertRows(QModelIndex(), row, row)

            self._items.append(job)

            if key:
                self._job_row_map[key] = row

            self.endInsertRows()

        # ------------------------------------------------
        # JOB UPDATE EVENTS
        # ------------------------------------------------

        elif event_type in (
            "job_progress",
            "job_finished",
            "job_failed",
            "job_updated",
        ):

            job = payload.get("job")
            if not job:
                return

            key = self._normalize_path(getattr(job, "source_path", None))

            row = self._job_row_map.get(key)

            if row is None or row >= len(self._items):
                return

            index = self.index(row)

            self.dataChanged.emit(
                index,
                index,
                [
                    self.ROLE_STATUS,
                    self.ROLE_PROGRESS,
                    self.ROLE_CODEC,
                    self.ROLE_RESOLUTION,
                ],
            )

        # ------------------------------------------------
        # CLEAR ALL
        # ------------------------------------------------

        elif event_type == "clear_all_jobs":

            if not self._items:
                return

            self.beginResetModel()
            self._items.clear()
            self._job_row_map.clear()
            self.endResetModel()


        # ------------------------------------------------
        # REMOVE SINGLE JOB
        # ------------------------------------------------

        elif event_type == "job_remove_requested":

            job = payload if not isinstance(payload, dict) else payload.get("job")

            if not job:
                return

            key = self._normalize_path(getattr(job, "source_path", None))
            row = self._job_row_map.get(key)

            if row is None or row >= len(self._items):
                return

            self.beginRemoveRows(QModelIndex(), row, row)
            del self._items[row]
            self.endRemoveRows()

            self._rebuild_row_map()

        # ------------------------------------------------
        # REMOVE INVALID
        # ------------------------------------------------

        elif event_type == "remove_invalid_requested":

            invalid_rows = []

            for i, item in enumerate(self._items):
                status = getattr(item, "status", "").upper()
                if status in ("ERROR", "FAILED", "INVALID"):
                    invalid_rows.append(i)

            if not invalid_rows:
                return

            for row in reversed(invalid_rows):

                self.beginRemoveRows(QModelIndex(), row, row)
                del self._items[row]
                self.endRemoveRows()

            self._rebuild_row_map()

        # ------------------------------------------------
        # CONFIGURATION CHANGED
        # ------------------------------------------------

        elif event_type == "configuration_changed":

            try:
                from app.core.output_naming import generate_output_path

                for row, job in enumerate(self._items):

                    source = getattr(job, "source_path", None)

                    if source:
                        job.output_path = generate_output_path(source)

                        index = self.index(row)

                        self.dataChanged.emit(
                            index,
                            index,
                            [self.ROLE_FILE_NAME],
                        )

            except Exception:
                pass

