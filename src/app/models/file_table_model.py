from PySide6.QtCore import Qt, QAbstractTableModel
import os

AUDIO_EXT = (".mp3",".aac",".wav",".flac",".ogg",".m4a",".wma",".opus",".alac")

def format_size(path):
    try:
        s = os.path.getsize(path)
        for unit in ["B","KB","MB","GB"]:
            if s < 1024:
                return f"{s:.0f} {unit}"
            s /= 1024
        return f"{s:.1f} TB"
    except:
        return ""


class FileTableModel(QAbstractTableModel):

    headers = ["Arquivo","Tipo","Tamanho"]

    def __init__(self, files):
        super().__init__()
        self.files = files

        # persist sorting state
        self._sort_column = 0
        self._sort_order = Qt.AscendingOrder

    # ------------------------------------------------
    # Basic model API
    # ------------------------------------------------

    def rowCount(self, parent=None):
        return len(self.files)

    def columnCount(self, parent=None):
        return 3

    def data(self, index, role):

        if not index.isValid():
            return None

        file = self.files[index.row()]

        if role == Qt.DisplayRole:

            if index.column() == 0:
                return os.path.basename(file)

            if index.column() == 1:
                ext = os.path.splitext(file)[1].lower()
                return "Áudio" if ext in AUDIO_EXT else "Vídeo"

            if index.column() == 2:
                return format_size(file)

        if role == Qt.TextAlignmentRole:

            if index.column() == 0:
                return Qt.AlignLeft | Qt.AlignVCenter

            if index.column() == 1:
                return Qt.AlignCenter | Qt.AlignVCenter

            if index.column() == 2:
                return Qt.AlignRight | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role):

        if orientation == Qt.Horizontal:

            if role == Qt.DisplayRole:
                return self.headers[section]

            if role == Qt.TextAlignmentRole:

                if section == 0:
                    return Qt.AlignLeft | Qt.AlignVCenter

                if section == 1:
                    return Qt.AlignCenter | Qt.AlignVCenter

                if section == 2:
                    return Qt.AlignRight | Qt.AlignVCenter

        return None

    # ------------------------------------------------
    # Sorting
    # ------------------------------------------------

    def sort(self, column, order):

        self._sort_column = column
        self._sort_order = order

        reverse = order == Qt.DescendingOrder

        if column == 0:  # Arquivo

            self.files.sort(
                key=lambda f: os.path.basename(f).lower(),
                reverse=reverse
            )

        elif column == 1:  # Tipo

            def file_type(f):
                ext = os.path.splitext(f)[1].lower()
                return 0 if ext in AUDIO_EXT else 1

            self.files.sort(key=file_type, reverse=reverse)

        elif column == 2:  # Tamanho

            def size(f):
                try:
                    return os.path.getsize(f)
                except:
                    return 0

            self.files.sort(key=size, reverse=reverse)

        self.layoutChanged.emit()

    # ------------------------------------------------
    # Utility to reapply sorting if files list changes
    # ------------------------------------------------

    def refresh(self):
        """
        Call this if the underlying file list changes but the model instance remains.
        It reapplies the last sorting rule.
        """
        self.sort(self._sort_column, self._sort_order)
