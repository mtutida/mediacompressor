from interaction_model.event_bridge import event_bridge

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedLayout

from ui.global_bar import GlobalBarWidget
from ui.context_bar import SelectionActionBarWidget
from ui.context_bar_widget import ContextBarWidget
from ui.file_list_container import FileListContainer
from ui.execution_footer import ExecutionFooterWidget
from ui.global_progress import GlobalProgressWidget
from ui.configuration_overlay import ConfigurationOverlay
from ui.file_list_model import FileListModel
from ui.selection_controller import SelectionController
from core.app_version import APP_NAME, APP_PHASE, APP_VERSION


class AppShell(QWidget):

    def update_window_title(self):
        self.setWindowTitle(f"{APP_NAME} — FASE {APP_PHASE} — v{APP_VERSION}")
    
    
    def __init__(self):
        super().__init__()
        event_bridge.subscribe(self._on_app_event)

        base_layout = QVBoxLayout(self)
        base_layout.setSpacing(0)
        base_layout.setContentsMargins(0,0,0,0)
        base_layout.setSpacing(0)

        self.global_bar = GlobalBarWidget()
        self.selection_bar = SelectionActionBarWidget()
        self.context_bar = ContextBarWidget()
        self.file_list_container = FileListContainer()
        self.file_list = self.file_list_container.file_list
        self.file_list.setModel(FileListModel())
        self.selection_controller = SelectionController(self.file_list)
        self.global_progress = GlobalProgressWidget()
        
        self.execution_footer = ExecutionFooterWidget()

        
        # content container to control lateral alignment
        content = QWidget()
        content.setObjectName("MainContent")
        content_layout = QVBoxLayout(content)

        # container that receives lateral margins (does NOT include progress strip)
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(2,0,2,0)
        main_layout.setSpacing(0)
        content_layout.setContentsMargins(0,0,0,0)
        content_layout.setSpacing(0)

        main_layout.addWidget(self.global_bar)
        
        middle_container = QWidget()
        middle_layout = QVBoxLayout(middle_container)
        middle_layout.setContentsMargins(6,0,6,0)
        middle_layout.setSpacing(0)

        middle_layout.addWidget(self.file_list_container, 1)
        middle_layout.addWidget(self.selection_bar)
        middle_layout.addWidget(self.context_bar)

        main_layout.addWidget(middle_container)

        main_layout.addWidget(self.execution_footer)
        content_layout.addWidget(main_container)
        content_layout.addWidget(self.global_progress)

        base_layout.addWidget(content)


        

        
        self.setStyleSheet("""

/* stronger hover visibility for toolbar/footer buttons */
QPushButton:hover {
    background-color: rgba(255,255,255,0.18);
}

        QWidget#MainContent{
            border:2px solid #3a3a3a;
            border-top:none;
        }
        """)

        self.update_window_title()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def close_configuration(self):
        self.overlay.hide()
    def open_configuration(self):
        dialog = ConfigurationOverlay(self)
        dialog.exec()



    def _on_app_event(self, event_type, payload):
        from PySide6.QtWidgets import QApplication
        if event_type == "shutdown_requested":
            QApplication.quit()
