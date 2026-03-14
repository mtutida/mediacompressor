from PySide6.QtCore import QObject


class SelectionController(QObject):
    """Controls selection state of FileList (FASE 15.3)"""

    def __init__(self, file_list):
        super().__init__()

        self.file_list = file_list
        self.selected_rows = []
        self.expanded_file_id = None

        self._connect_selection_model()

    def _connect_selection_model(self):

        sel_model = self.file_list.selectionModel()

        if sel_model:
            sel_model.selectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, selected, deselected):

        indexes = self.file_list.selectedIndexes()

        # guardar apenas rows (mais seguro que QModelIndex)
        self.selected_rows = sorted({i.row() for i in indexes})

    def clear_selection(self):
        self.file_list.clearSelection()

    def get_selected_rows(self):
        return list(self.selected_rows)

    def has_selection(self):
        return bool(self.selected_rows)
    