from app.interaction_model.event_bridge import event_bridge
from app.ui.file_list_model import FileListModel


class ExecutionController:

    def __init__(self):
        self.file_list = None
        self.selection_controller = None

    def set_context(self, file_list, selection_controller):
        self.file_list = file_list
        self.selection_controller = selection_controller

    # ------------------------
    # Compress
    # ------------------------

    def compress_selected(self):

        rows = self.selection_controller.get_selected_rows()

        if not rows:
            return

        model = self.file_list.model()

        for r in rows:
            index = model.index(r)
            job = model.data(index, FileListModel.ROLE_JOB)

            if job:
                event_bridge.emit("job_run_requested", {"job": job})

    def compress_all(self):

        model = self.file_list.model()
        total = model.rowCount()

        for r in range(total):
            index = model.index(r)
            job = model.data(index, FileListModel.ROLE_JOB)

            if job:
                event_bridge.emit("job_run_requested", {"job": job})

    # ------------------------
    # Cancel
    # ------------------------

    def cancel_selected(self):

        rows = self.selection_controller.get_selected_rows()

        if not rows:
            return

        model = self.file_list.model()

        for r in rows:
            index = model.index(r)
            job = model.data(index, FileListModel.ROLE_JOB)

            if job:
                event_bridge.emit("job_cancel_requested", job)

    def cancel_all(self):
        event_bridge.emit("cancel_all_requested", None)


execution_controller = ExecutionController()