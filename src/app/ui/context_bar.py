from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

BTN_HEIGHT = 24
BTN_WIDTH = 132


class SelectionActionBarWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SelectionActionBarWidget")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 1, 8, 1)
        layout.setSpacing(6)

        self.title_label = QLabel("Lista de arquivos")
        self.title_label.setObjectName("SelectionActionBarTitle")
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.title_label.setStyleSheet("font-weight: 600;")

        # Futuro: reintroduzir botão "Perfis" aqui quando o painel de perfis existir.
        self.btn_delete = QPushButton("Excluir")
        self.btn_clear_selection = QPushButton("Limpar seleção")

        buttons = [
            self.btn_delete,
            self.btn_clear_selection,
        ]

        for b in buttons:
            b.setFixedHeight(BTN_HEIGHT)

        self.btn_delete.setMinimumWidth(100)
        self.btn_clear_selection.setMinimumWidth(120)

        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_clear_selection)

        self.setLayout(layout)

        self.set_has_selection(False)

    def set_has_selection(self, has_selection):
        enabled = bool(has_selection)
        self.btn_delete.setEnabled(enabled)
        self.btn_clear_selection.setEnabled(enabled)


ContextBarWidget = SelectionActionBarWidget
