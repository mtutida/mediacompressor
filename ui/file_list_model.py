
from interaction_model.event_bridge import event_bridge
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex

class FileListModel(QAbstractListModel):

    ROLE_JOB = Qt.UserRole + 1
    ROLE_FILE_NAME = Qt.UserRole + 2
    ROLE_STATUS = Qt.UserRole + 3
    ROLE_PROGRESS = Qt.UserRole + 4
    ROLE_CODEC = Qt.UserRole + 5
    ROLE_RESOLUTION = Qt.UserRole + 6

    def __init__(self, interaction_model=None):
        super().__init__()
        self._items=[]
        self._interaction_model=interaction_model
        event_bridge.subscribe(self._on_event)

    def rowCount(self,parent=QModelIndex()):
        return len(self._items)

    def data(self,index,role):

        if not index.isValid():
            return None

        item=self._items[index.row()]

        if role==Qt.DisplayRole:
            return getattr(item,"file_name","unknown")

        if role==self.ROLE_JOB:
            return item

        if role==self.ROLE_FILE_NAME:
            return getattr(item,"file_name","unknown")

        if role==self.ROLE_STATUS:
            return getattr(item,"status","pending")

        if role==self.ROLE_PROGRESS:
            return getattr(item,"progress",0)

        if role==self.ROLE_CODEC:
            return getattr(item,"codec","?")

        if role==self.ROLE_RESOLUTION:
            return getattr(item,"resolution","?")

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

    def _on_event(self,event_type,payload):

        if event_type=="job_enqueued":
            job=payload.get("job")
            self.beginInsertRows(QModelIndex(),len(self._items),len(self._items))
            self._items.append(job)
            self.endInsertRows()

        elif event_type in ("job_progress","job_finished","job_failed","job_updated"):
            self.layoutChanged.emit()
        elif event_type == "clear_all_jobs":
            if not self._items:
                return
            self.beginResetModel()
            self._items.clear()
            self.endResetModel()

        elif event_type == "remove_invalid_requested":

            invalid_rows = []

            for i, item in enumerate(self._items):
                status = getattr(item, "status", "").upper()
                if status in ("ERROR", "FAILED", "INVALID"):
                    invalid_rows.append(i)

            for row in reversed(invalid_rows):
                self.beginRemoveRows(QModelIndex(), row, row)
                del self._items[row]
                self.endRemoveRows()


    def update_job(self,job):
        self.layoutChanged.emit()
