
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton
from PySide6.QtCore import Qt
from app.interaction_model.event_bridge import event_bridge


class ContextBarWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("ContextBarWidget")
        self.setFixedHeight(28)

        # registry of jobs
        self._jobs = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 3, 12, 3)
        layout.setSpacing(6)

        self.label = QLabel()
        self.label.setContentsMargins(0, 0, 4, 0)

        layout.addWidget(self.label)
        layout.addStretch()

        # maintenance action
        self.btn_remove_invalid = QToolButton()
        self.btn_remove_invalid.setText("Remover inválidos")
        self.btn_remove_invalid.setAutoRaise(True)
        self.btn_remove_invalid.setFixedHeight(20)

        layout.addWidget(self.btn_remove_invalid)

        self.btn_remove_invalid.clicked.connect(self._remove_invalid)

        # subscribe to global bridge
        event_bridge.subscribe(self._on_event)

        self._update_stats()

    # ------------------------------------------------

    def mousePressEvent(self, event):
        # Ignore clicks on the "remove invalid" button
        if self.btn_remove_invalid.geometry().contains(event.pos()):
            super().mousePressEvent(event)
            return

        # Click on empty area → clear selection
        event_bridge.emit("clear_selection_requested", None)
        super().mousePressEvent(event)

    # ------------------------------------------------

    def _remove_invalid(self):
        event_bridge.emit("remove_invalid_requested", None)

    # ------------------------------------------------
    # Event bridge
    # ------------------------------------------------

    def _on_event(self, event_type, payload):

        if event_type == "clear_all_jobs":
            self._jobs.clear()
            self._update_stats()
            return

        if not payload:
            return

        if event_type not in ("job_enqueued", "job_updated"):
            return

        job = payload.get("job")
        if not job:
            return

        key = getattr(job, "source_path", None) or id(job)
        self._jobs[key] = job

        self._update_stats()

    # ------------------------------------------------

    def _resolve_state(self, total, active, queued, done, error):

        if total == 0:
            return "Ocioso", "palette(mid)"

        if error > 0:
            return "Com erro", "palette(highlight)"

        if active > 0:
            return "Processando", "palette(highlight)"

        if queued > 0:
            return "Na fila", "palette(highlight)"

        if done == total:
            return "Concluído", "palette(highlight)"

        return "Ocioso", "palette(mid)"

    # ------------------------------------------------

    def _update_stats(self):

        total = len(self._jobs)

        active = 0
        queued = 0
        done = 0
        error = 0
        cancelled = 0

        for job in self._jobs.values():

            status = str(getattr(job, "status", "")).upper()

            if status in ("ANALYZING", "PROCESSING", "RUNNING"):
                active += 1

            elif status in ("READY", "QUEUED"):
                queued += 1

            elif status in ("DONE", "FINISHED", "COMPLETED"):
                done += 1

            elif status in ("ERROR", "FAILED"):
                error += 1

            elif status == "CANCELLED":
                cancelled += 1

        state, color = self._resolve_state(total, active, queued, done, error)

        dot = f'<span style="color:{color};font-size:14px;">●</span>'

        text = (
            f"{dot} {state}"
            f" | Itens: {total}"
            f" | Ativo: {active}"
            f" | Fila: {queued}"
            f" | Concluído: {done}"
            f" | Cancelado: {cancelled}"
            f" | Erro: {error}"
        )

        self.label.setText(text)
