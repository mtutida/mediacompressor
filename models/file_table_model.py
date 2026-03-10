
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
                return Qt.AlignCenter
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
