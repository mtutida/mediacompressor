from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton
from interaction_model.event_bridge import event_bridge

class ContextBarWidget(QFrame):

    def __init__(self,parent=None):
        super().__init__(parent)

        self.setObjectName("ContextBarWidget")
        self.setFixedHeight(28)

        layout=QHBoxLayout(self)
        layout.setContentsMargins(12,3,12,3)
        layout.setSpacing(6)

        self.label=QLabel("Ocioso | 0 itens • 0 ativo • 0 na fila • 0 concluído • 0 erro")
        self.label.setContentsMargins(0,0,4,0)

        layout.addWidget(self.label)
        layout.addStretch()

        # Queue maintenance action
        self.btn_remove_invalid = QToolButton()
        self.btn_remove_invalid.setText("Remover inválidos")
        self.btn_remove_invalid.setAutoRaise(True)
        self.btn_remove_invalid.setFixedHeight(20)

        layout.addWidget(self.btn_remove_invalid)

        self.btn_remove_invalid.clicked.connect(self._remove_invalid)

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
            color:#4aa3ff; font-weight:500;
        }

        QToolButton:hover{
            background:#3a3a3a;
            border-radius:3px;
            color:#79c0ff;
        }
        """)

    def _remove_invalid(self):
        event_bridge.emit("remove_invalid_requested", None)
