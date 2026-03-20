from PySide6.QtWidgets import QMessageBox
import os

from app.core.output_naming import generate_output_path
from app.interaction_model.event_bridge import event_bridge
from app.ui.file_list_model import FileListModel


class ExecutionController:

    def __init__(self):
        self.file_list = None
        self.selection_controller = None

    def set_context(self, file_list, selection_controller):
        self.file_list = file_list
        self.selection_controller = selection_controller

    def _collect_jobs(self, rows):
        if not rows or not self.file_list:
            return []

        model = self.file_list.model()
        jobs = []

        for r in rows:
            index = model.index(r)
            job = model.data(index, FileListModel.ROLE_JOB)
            if job:
                jobs.append(job)

        return jobs

    def _ask_create_directory(self, output_dir):
        msg = QMessageBox(self.file_list)
        msg.setWindowTitle("Criar pasta de destino")
        msg.setIcon(QMessageBox.Question)
        msg.setText(
            f"A pasta de destino não existe:\n\n{output_dir}\n\nDeseja criá-la?"
        )
        criar_btn = msg.addButton("Criar", QMessageBox.AcceptRole)
        msg.addButton("Cancelar", QMessageBox.RejectRole)
        msg.setDefaultButton(criar_btn)
        msg.exec()
        return msg.clickedButton() is criar_btn

    def _ensure_output_directories(self, jobs):
        checked_dirs = set()

        for job in jobs:
            output_path = generate_output_path(job.source_path)
            output_dir = os.path.dirname(output_path)

            if not output_dir or output_dir in checked_dirs:
                continue

            checked_dirs.add(output_dir)

            if os.path.exists(output_dir):
                continue

            if not self._ask_create_directory(output_dir):
                return False

            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as exc:
                QMessageBox.critical(
                    self.file_list,
                    "Falha ao criar pasta",
                    f"Não foi possível criar a pasta de destino.\n\n{output_dir}\n\nErro: {exc}",
                )
                return False

        return True

    def run_jobs(self, jobs):
        if not jobs:
            return

        if not self._ensure_output_directories(jobs):
            return

        for job in jobs:
            event_bridge.emit("job_run_requested", {"job": job})

    def run_job(self, job):
        if not job:
            return
        self.run_jobs([job])

    # ------------------------
    # Compress
    # ------------------------

    def compress_selected(self):
        rows = self.selection_controller.get_selected_rows()
        self.run_jobs(self._collect_jobs(rows))

    def compress_all(self):
        if not self.file_list:
            return

        model = self.file_list.model()
        self.run_jobs(self._collect_jobs(range(model.rowCount())))

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
