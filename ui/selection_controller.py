from PySide6.QtCore import QObject


class SelectionController(QObject):
    """Controls selection state of FileList (FASE 15.3)"""

    def __init__(self, file_list):
        super().__init__()
        self.file_list = file_list
        self.selected_indexes = []
        self.expanded_file_id = None

        sel_model = self.file_list.selectionModel()
        if sel_model:
            sel_model.selectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, selected, deselected):
        self.selected_indexes = self.file_list.selectedIndexes()

    def clear_selection(self):
        self.file_list.clearSelection()

    def get_selected_rows(self):
        return [i.row() for i in self.selected_indexes]
