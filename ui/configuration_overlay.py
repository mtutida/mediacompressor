
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QPushButton
from ui.configuration_panel import ConfigurationPanelWidget
from ancillary.configuration import ConfigurationService


class ConfigurationOverlay(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("ConfigurationDialog")
        self.setWindowTitle("Preferências")
        self.setModal(True)
        self.resize(460, 500)

        layout = QVBoxLayout(self)

        self.panel = ConfigurationPanelWidget(self)
        layout.addWidget(self.panel)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.btn_defaults = QPushButton("Restaurar padrões")
        buttons.addButton(self.btn_defaults, QDialogButtonBox.ResetRole)

        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        self.btn_defaults.clicked.connect(self.panel.restore_defaults)

        layout.addWidget(buttons)

    def _accept(self):

        import os
        from PySide6.QtWidgets import QMessageBox
        from ancillary.configuration import ConfigurationService

        data = self.panel.collect_values()
        path = data["output_directory"]

        if not data["use_source_directory"] and path:

            if not os.path.exists(path):

                reply = QMessageBox.question(
                    self,
                    "Criar pasta",
                    """A pasta especificada não existe.

Deseja criá-la?""",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.No:
                    return

                try:
                    os.makedirs(path)
                except PermissionError:
                    QMessageBox.critical(
                        self,
                        "Permissão negada",
                        """Não foi possível criar a pasta.

Verifique permissões ou escolha outro caminho."""
                    )
                    return

        ConfigurationService.instance().update(**data)

        self.accept()
