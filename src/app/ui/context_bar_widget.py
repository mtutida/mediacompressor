
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QListView
from PySide6.QtCore import Qt, QTimer
from app.interaction_model.event_bridge import event_bridge


class ContextBarWidget(QFrame):

    ROLE_JOB = Qt.UserRole + 1

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("ContextBarWidget")
        self.setFixedHeight(28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 3, 12, 3)
        layout.setSpacing(6)

        self.label = QLabel()
        layout.addWidget(self.label)
        layout.addStretch()

        self.btn_remove_invalid = QToolButton()
        self.btn_remove_invalid.setText("Remover inválidos")
        self.btn_remove_invalid.setAutoRaise(True)
        self.btn_remove_invalid.setFixedHeight(20)
        layout.addWidget(self.btn_remove_invalid)

        self.btn_remove_invalid.clicked.connect(self._remove_invalid)

        # refresh when queue events occur
        event_bridge.subscribe(self._on_event)

        # safety refresh (covers cases where model changes without events)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_stats)
        self._timer.start(800)

        self.setStyleSheet("""
        QFrame#ContextBarWidget{
            background:#2b2b2b;
            border-left:1px solid #3a3a3a;
            border-right:1px solid #3a3a3a;
            border-bottom:1px solid #3a3a3a;
            border-bottom-left-radius:6px;
            border-bottom-right-radius:6px;
        }

        QLabel{
            font-size:12px;
            color:#c8c8c8;
        }

        QToolButton{
            padding:0px 6px;
            border:0px;
            background:transparent;
            color:#4aa3ff;
            font-weight:500;
        }

        QToolButton:hover{
            background:#3a3a3a;
            border-radius:3px;
            color:#79c0ff;
        }
        """)

        self._update_stats()

    # ------------------------------------------------

    def _remove_invalid(self):
        event_bridge.emit("remove_invalid_requested", None)

    # ------------------------------------------------

    def _on_event(self, event_type, payload):
        if event_type in (
            "job_enqueued",
            "job_updated",
            "job_removed",
            "queue_cleared",
        ):
            self._update_stats()

    # ------------------------------------------------

    def _get_file_list(self):
        window = self.window()
        if not window:
            return None
        return window.findChild(QListView, "FileList")

    # ------------------------------------------------

    def _resolve_state(self, total, active, queued, done, error):

        if total == 0:
            return "Ocioso", "#9a9a9a"

        if error > 0:
            return "Com erro", "#ff5f56"

        if active > 0:
            return "Processando", "#ffb020"

        if queued > 0:
            return "Na fila", "#4aa3ff"

        if done == total:
            return "Concluído", "#3fb950"

        return "Ocioso", "#9a9a9a"

    # ------------------------------------------------

    def _update_stats(self):

        file_list = self._get_file_list()
        if not file_list:
            return

        model = file_list.model()
        if not model:
            return

        total = model.rowCount()

        active = 0
        queued = 0
        done = 0
        error = 0

        for row in range(total):

            index = model.index(row, 0)
            job = index.data(self.ROLE_JOB)

            if not job:
                continue

            status = str(getattr(job, "status", "")).upper()

            if status in ("ANALYZING", "PROCESSING", "RUNNING"):
                active += 1

            elif status in ("READY", "QUEUED"):
                queued += 1

            elif status in ("DONE", "FINISHED", "COMPLETED"):
                done += 1

            elif status in ("ERROR", "FAILED"):
                error += 1

        state, color = self._resolve_state(total, active, queued, done, error)

        dot = f'<span style="color:{color};font-size:14px;">●</span>'

        text = (
            f"{dot} {state}"
            f"   |   Itens: {total}"
            f"   |   Ativo: {active}"
            f"   |   Fila: {queued}"
            f"   |   Concluído: {done}"
            f"   |   Erro: {error}"
        )

        self.label.setText(text)
