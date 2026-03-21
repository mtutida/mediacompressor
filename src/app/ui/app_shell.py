from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QWidget

from app.core.app_version import APP_NAME, APP_PHASE, APP_VERSION
from app.interaction_model.event_bridge import event_bridge
from app.interaction_model.execution_controller import execution_controller
from app.ui.configuration_overlay import ConfigurationOverlay
from app.ui.context_bar_widget import ContextBarWidget
from app.ui.execution_footer import ExecutionFooterWidget
from app.ui.file_list_container import FileListContainer
from app.ui.file_list_model import FileListModel
from app.ui.global_bar import GlobalBarWidget
from app.ui.global_progress import GlobalProgressWidget
from app.ui.selection_controller import SelectionController
from app.ui.toast_manager import ToastManager


class AppShell(QWidget):

    def __init__(self, ctx):
        super().__init__()

        self.ctx = ctx
        self.ctx.logger.info("AppShell initialized")

        event_bridge.subscribe(self._on_app_event)

        self._build_ui()

        self.toast = ToastManager(self)

        self.update_window_title()

        # Footer wiring
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
        self.context_bar = ContextBarWidget()

        self.file_list_container = FileListContainer()
        self.selection_bar = self.file_list_container.title_bar if hasattr(self.file_list_container, "title_bar") else None
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

        try:
            self.file_list.selectionModel().selectionChanged.connect(
                self._update_selection_bar_state
            )
        except Exception:
            pass

        self.selection_bar.btn_delete.clicked.connect(self._remove_selected_jobs)
        self.selection_bar.btn_clear_selection.clicked.connect(
            self.selection_controller.clear_selection
        )

        self.execution_footer = ExecutionFooterWidget()
        self.global_progress = GlobalProgressWidget()

        self.content = QWidget()
        self.content.setObjectName("MainContent")
        self.content.setAutoFillBackground(True)

        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        main_layout.addWidget(self.global_bar)

        middle_container = QWidget()
        middle_layout = QVBoxLayout(middle_container)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(6)

        middle_layout.addWidget(self.file_list_container, 1)
        middle_layout.addWidget(self.context_bar)

        main_layout.addWidget(middle_container)
        main_layout.addWidget(self.execution_footer)

        content_layout.addWidget(main_container)
        content_layout.addWidget(self.global_progress)

        self.base_layout.addWidget(self.content)

        self.setStyleSheet(
            """
            QWidget#MainContent {
                background: palette(alternate-base);
                border: 2px solid palette(midlight);
                border-top: none;
            }

            QFrame#GlobalBarWidget,
            QFrame#SelectionActionBarWidget,
            QFrame#ContextBarWidget,
            QFrame#ExecutionFooterWidget {
                background: palette(base);
                border: 1px solid palette(midlight);
                border-radius: 4px;
            }

            QFrame#GlobalBarWidget,
            QFrame#SelectionActionBarWidget,
            QFrame#ExecutionFooterWidget {
                padding: 2px;
            }

            QPushButton:hover {
                border: 1px solid palette(highlight);
                background: palette(midlight);
                border-radius: 4px;
            }
            """
        )

        self._update_footer_state()
        self._update_selection_bar_state()

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

    def _has_processing_jobs(self):

        model = self.file_list.model()
        total = model.rowCount()

        for r in range(total):
            index = model.index(r)
            job = model.data(index, FileListModel.ROLE_JOB)

            if job and getattr(job, "status", None) in ("PROCESSING", "RUNNING"):
                return True

        run_controller = getattr(self.ctx, "run_controller", None)

        if not run_controller:
            return False

        if getattr(run_controller, "jobs", None):
            return True

        queue = getattr(run_controller, "_queue", None)

        if queue:
            return len(queue) > 0

        return False

    def _confirm_shutdown_while_processing(self):

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Encerrar durante processamento")
        msg.setText("Há compressão em andamento.\nDeseja sair mesmo assim?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        yes_button = msg.button(QMessageBox.Yes)
        no_button = msg.button(QMessageBox.No)

        if yes_button is not None:
            yes_button.setText("Sim")

        if no_button is not None:
            no_button.setText("Não")

        return msg.exec() == QMessageBox.Yes

    def closeEvent(self, event):
        if self._has_processing_jobs() and not self._confirm_shutdown_while_processing():
            event.ignore()
            return

        super().closeEvent(event)

    def _on_app_event(self, event_type, payload):

        if event_type == "shutdown_requested":
            self.close()

        elif event_type == "clear_all_requested":

            if self._has_processing_jobs():
                self._warn_clear_while_processing()
                return

            event_bridge.emit("clear_all_jobs", None)

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

            path = getattr(job, "output_path", None) or getattr(
                job, "source_path", None
            )
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

        # LIST EMPTY → disable everything except Exit
        if total == 0:
            self.execution_footer.btn_compress.setEnabled(False)
            self.execution_footer.btn_compress_all.setEnabled(False)
            self.execution_footer.btn_cancel.setEnabled(False)
            self.execution_footer.btn_cancel_all.setEnabled(False)
            self.execution_footer.btn_clear_all.setEnabled(False)
            return

        # LIST HAS ITEMS → enable buttons again
        self.execution_footer.btn_compress.setEnabled(True)
        self.execution_footer.btn_compress_all.setEnabled(True)
        self.execution_footer.btn_cancel.setEnabled(True)
        self.execution_footer.btn_cancel_all.setEnabled(True)
        self.execution_footer.btn_clear_all.setEnabled(True)

        # detect if processing
        processing = False

        for r in range(total):
            index = model.index(r)
            job = model.data(index, FileListModel.ROLE_JOB)

            if job and getattr(job, "status", None) in ("PROCESSING", "RUNNING"):
                processing = True
                break

        self.execution_footer.btn_clear_all.setEnabled(not processing)
        self.execution_footer.set_processing_state(processing)


    def _get_selected_jobs(self):

        jobs = []
        seen = set()

        for index in self.file_list.selectedIndexes():
            job = self.file_list.model().data(index, FileListModel.ROLE_JOB)
            if not job:
                continue

            marker = id(job)
            if marker in seen:
                continue

            seen.add(marker)
            jobs.append(job)

        return jobs

    def _remove_selected_jobs(self):

        for job in self._get_selected_jobs():
            event_bridge.emit("job_remove_requested", job)

    def _update_selection_bar_state(self, *args):

        has_selection = bool(self._get_selected_jobs())
        self.selection_bar.btn_delete.setEnabled(has_selection)
        self.selection_bar.btn_clear_selection.setEnabled(has_selection)

    def changeEvent(self, event):
        from PySide6.QtCore import QEvent

        if event.type() == QEvent.PaletteChange:
            # Theme changed (Windows light/dark)
            self._reapply_theme()
        super().changeEvent(event)

    def _reapply_theme(self):
        from PySide6.QtWidgets import QApplication

        from app.ui.ui_palette import UIPalette

        UIPalette.reload()

        app = QApplication.instance()

        for w in app.allWidgets():
            w.style().unpolish(w)
            w.style().polish(w)
            w.update()
