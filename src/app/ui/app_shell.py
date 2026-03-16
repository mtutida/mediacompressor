
from PySide6.QtWidgets import QWidget, QVBoxLayout

from app.ui.toast_manager import ToastManager
from app.interaction_model.event_bridge import event_bridge

from app.ui.global_bar import GlobalBarWidget
from app.ui.context_bar import SelectionActionBarWidget
from app.ui.context_bar_widget import ContextBarWidget
from app.ui.file_list_container import FileListContainer
from app.ui.execution_footer import ExecutionFooterWidget
from app.ui.global_progress import GlobalProgressWidget
from app.ui.configuration_overlay import ConfigurationOverlay
from app.ui.file_list_model import FileListModel
from app.ui.selection_controller import SelectionController
from app.interaction_model.execution_controller import execution_controller


from app.core.app_version import APP_NAME, APP_PHASE, APP_VERSION


class AppShell(QWidget):

    def __init__(self, ctx):
        super().__init__()

        self.ctx = ctx
        self.ctx.logger.info("AppShell initialized")

        event_bridge.subscribe(self._on_app_event)

        self._build_ui()

        self.toast = ToastManager(self)

        self.update_window_title()

        # --- Footer button wiring ---
        self.execution_footer.btn_compress.clicked.connect(
            execution_controller.compress_selected
        )

        self.execution_footer.btn_compress_all.clicked.connect(
            execution_controller.compress_all
        )

        self.execution_footer.btn_cancel.clicked.connect(
            execution_controller.cancel_selected
        )

        self.execution_footer.btn_cancel_all.clicked.connect(
            execution_controller.cancel_all
        )

    def _build_ui(self):

        self.base_layout = QVBoxLayout(self)
        self.base_layout.setContentsMargins(0, 0, 0, 0)
        self.base_layout.setSpacing(0)

        self.global_bar = GlobalBarWidget()
        self.selection_bar = SelectionActionBarWidget()
        self.context_bar = ContextBarWidget()

        self.file_list_container = FileListContainer()
        self.file_list = self.file_list_container.file_list
        self.file_list.setModel(FileListModel())

        model = self.file_list.model()

        try:
            model.dataChanged.connect(self._update_footer_state)
            model.rowsInserted.connect(self._update_footer_state)
            model.rowsRemoved.connect(self._update_footer_state)
            model.modelReset.connect(self._update_footer_state)
        except Exception:
            pass

        self.selection_controller = SelectionController(self.file_list)
        execution_controller.set_context(self.file_list, self.selection_controller)

        self.execution_footer = ExecutionFooterWidget()
        self.global_progress = GlobalProgressWidget()

        self.content = QWidget()
        self.content.setObjectName("MainContent")

        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(2, 0, 2, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.global_bar)

        middle_container = QWidget()
        middle_layout = QVBoxLayout(middle_container)
        middle_layout.setContentsMargins(6, 0, 6, 0)
        middle_layout.setSpacing(0)

        middle_layout.addWidget(self.file_list_container, 1)
        middle_layout.addWidget(self.selection_bar)
        middle_layout.addWidget(self.context_bar)

        main_layout.addWidget(middle_container)
        main_layout.addWidget(self.execution_footer)

        content_layout.addWidget(main_container)
        content_layout.addWidget(self.global_progress)

        self.base_layout.addWidget(self.content)

        self.setStyleSheet("""
        QPushButton:hover {
            background-color: rgba(255,255,255,0.18);
        }

        QWidget#MainContent{
            border:2px solid #3a3a3a;
            border-top:none;
        }
        """)

        # ensure correct initial state
        self._update_footer_state()

    def update_window_title(self):
        self.setWindowTitle(f"{APP_NAME} — FASE {APP_PHASE} — v{APP_VERSION}")

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def close_configuration(self):
        if hasattr(self, "overlay"):
            self.overlay.hide()

    def open_configuration(self):
        dialog = ConfigurationOverlay(self)
        dialog.exec()

    def _on_app_event(self, event_type, payload):
        from PySide6.QtWidgets import QApplication

        if event_type == "shutdown_requested":
            QApplication.quit()

        elif event_type == "duplicate_files_ignored":

            count = payload.get("count", 0)

            if count <= 0:
                return

            if count == 1:
                msg = "Arquivo já estava na lista"
            else:
                msg = f"{count} arquivos já estavam na lista"

            self.toast.show(msg)

        elif event_type == "job_open_folder_requested":

            job = payload
            if not job:
                return

            import os
            import subprocess

            path = getattr(job, "output_path", None) or getattr(job, "source_path", None)
            if not path:
                return

            path = os.path.normpath(path)

            try:
                if os.path.exists(path):
                    subprocess.Popen(["explorer", "/select,", path])
                else:
                    folder = os.path.dirname(path)
                    if os.path.exists(folder):
                        subprocess.Popen(["explorer", folder])
            except Exception:
                pass

        elif event_type == "files_dropped":

            paths = payload.get("paths", []) if payload else []

            if not paths:
                return

            for p in paths:
                try:
                    self.global_bar._create_job(p)
                except Exception:
                    pass

    def _update_footer_state(self):

        model = self.file_list.model()
        total = model.rowCount()

        # disable buttons if list empty
        if total == 0:
            self.execution_footer.btn_compress.setEnabled(False)
            self.execution_footer.btn_compress_all.setEnabled(False)
            self.execution_footer.btn_cancel.setEnabled(False)
            self.execution_footer.btn_cancel_all.setEnabled(False)
            self.execution_footer.btn_clear_all.setEnabled(False)
            return

        # enable buttons if list has items
        self.execution_footer.btn_compress.setEnabled(True)
        self.execution_footer.btn_compress_all.setEnabled(True)
        self.execution_footer.btn_clear_all.setEnabled(True)

        processing = False

        for r in range(total):
            index = model.index(r)
            job = model.data(index, FileListModel.ROLE_JOB)

            if job and getattr(job, "status", None) in ("PROCESSING", "RUNNING"):
                processing = True
                break

        self.execution_footer.set_processing_state(processing)
