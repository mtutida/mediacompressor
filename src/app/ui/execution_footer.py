from app.interaction_model.event_bridge import event_bridge

from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QSizePolicy

BTN_WIDTH = 210

class ExecutionFooterWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ExecutionFooterWidget")
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("QFrame { background: transparent; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4,4,4,4)
        layout.setSpacing(3)

        self.btn_compress = QPushButton("Comprimir")
        self.btn_compress_all = QPushButton("Comprimir Todos")
        self.btn_cancel = QPushButton("Cancelar Selecionados")
        self.btn_cancel_all = QPushButton("Cancelar Todos")
        self.btn_cancel.hide()
        self.btn_cancel_all.hide()
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

        
        
        for b in [
            self.btn_compress,
            self.btn_compress_all,
            self.btn_cancel,
            self.btn_cancel_all,
            self.btn_clear_all
        ]:
            b.setMinimumWidth(120)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(self.btn_compress)
        layout.addWidget(self.btn_compress_all)
        layout.addWidget(self.btn_cancel)
        layout.addWidget(self.btn_cancel_all)
        layout.addWidget(self.btn_clear_all)

        

        layout.addWidget(self.btn_exit)

        self.btn_clear_all.clicked.connect(self._clear_all)
        self.btn_cancel.clicked.connect(lambda: event_bridge.emit("cancel_selected_requested", None))
        self.btn_cancel_all.clicked.connect(lambda: event_bridge.emit("cancel_all_requested", None))

        self.btn_exit.clicked.connect(self._request_shutdown)

        self.setLayout(layout)

    def _request_shutdown(self):
        event_bridge.emit("shutdown_requested", None)


    def _clear_all(self):
        event_bridge.emit("clear_all_jobs", None)

    def set_processing_state(self, processing: bool):
        if processing:
            self.btn_compress.hide()
            self.btn_compress_all.hide()
            self.btn_cancel.show()
            self.btn_cancel_all.show()
        else:
            self.btn_cancel.hide()
            self.btn_cancel_all.hide()
            self.btn_compress.show()
            self.btn_compress_all.show()
