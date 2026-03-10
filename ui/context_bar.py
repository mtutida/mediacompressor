
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton

BTN_WIDTH = 180

class SelectionActionBarWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContextBarWidget")
        self.setFrameShape(QFrame.StyledPanel)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6,4,6,4)
        layout.setSpacing(12)

        self.btn_config = QPushButton("Configurar")
        self.btn_enqueue = QPushButton("Enfileirar")
        self.btn_delete = QPushButton("Excluir")
        self.btn_clear_selection = QPushButton("Cancelar seleção")

        buttons=[
            self.btn_config,
            self.btn_enqueue,
            self.btn_delete,
            self.btn_clear_selection
        ]

        for b in buttons:
            b.setFixedWidth(BTN_WIDTH)

        layout.addWidget(self.btn_config)
        layout.addWidget(self.btn_enqueue)
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.btn_clear_selection)

        layout.addStretch()

        self.setLayout(layout)

        # hidden until selection exists
        self.setVisible(False)

# backward compatibility alias
ContextBarWidget = SelectionActionBarWidget
