from app.interaction_model.event_bridge import event_bridge

from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QSizePolicy

BTN_WIDTH = 210

class ExecutionFooterWidget(QFrame):
    def __init__(self, file_list, parent=None):
        super().__init__(parent)
        self.file_list = file_list
        self.setObjectName("ExecutionFooterWidget")
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("QFrame { background: transparent; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4,4,4,4)
        layout.setSpacing(3)

        self.btn_compress = QPushButton("Comprimir")
        self.btn_compress_all = QPushButton("Comprimir Todos")
        self.btn_clear_all = QPushButton("Limpar Tudo")
        self.btn_exit = QPushButton("Sair")
        self.btn_exit.setFixedWidth(90)
        self.btn_exit.setMinimumHeight(36)

        buttons=[
            self.btn_compress,
            self.btn_compress_all,
            self.btn_clear_all,
            self.btn_exit
        ]

        
        
        for b in [self.btn_compress, self.btn_compress_all, self.btn_clear_all]:
            b.setMinimumWidth(120)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(self.btn_compress)
        layout.addWidget(self.btn_compress_all)
        layout.addWidget(self.btn_clear_all)

        layout.addWidget(self.btn_exit)

        self.btn_compress.clicked.connect(self._compress_selected)
        self.btn_compress_all.clicked.connect(self._compress_all)


        self.btn_clear_all.clicked.connect(self._clear_all)
        self.btn_exit.clicked.connect(self._request_shutdown)


        self.setLayout(layout)

    def _request_shutdown(self):
        event_bridge.emit("shutdown_requested", None)


    def _clear_all(self):
        event_bridge.emit("clear_all_jobs", None)

    def _compress_selected(self):

        indexes = self.file_list.selectedIndexes()

        for index in indexes:
            job = index.data(self.file_list.delegate.ROLE_JOB)
            if job:
                event_bridge.emit("job_run_requested", job)


    def _compress_all(self):

        model = self.file_list.model()

        for row in range(model.rowCount()):
            index = model.index(row, 0)
            job = index.data(self.file_list.delegate.ROLE_JOB)

            if job:
                event_bridge.emit("job_run_requested", job)

