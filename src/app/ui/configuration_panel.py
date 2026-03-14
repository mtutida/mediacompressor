
from PySide6.QtWidgets import (
    QFrame,QVBoxLayout,QLabel,QCheckBox,
    QHBoxLayout,QLineEdit,QPushButton,QFileDialog,
    QComboBox
)
from app.ancillary.configuration import ConfigurationService, AppConfiguration
import os
import datetime



class SuffixLineEdit(QLineEdit):

    DEFAULT_TEXT = "_compactado | ou digite seu próprio sufixo"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText(self.DEFAULT_TEXT)

    def focusInEvent(self, event):
        if self.text() == self.DEFAULT_TEXT:
            self.clear()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        if self.text().strip() == "":
            self.setText(self.DEFAULT_TEXT)
        super().focusOutEvent(event)

    def restore_default(self):
        self.setText(self.DEFAULT_TEXT)


class ConfigurationPanelWidget(QFrame):

    def __init__(self,parent=None):
        super().__init__(parent)

        self.setObjectName("ConfigurationPanelWidget")
        self.setFrameShape(QFrame.StyledPanel)

        self.service = ConfigurationService.instance()

        layout = QVBoxLayout(self)

        title = QLabel("Preferências")
        layout.addWidget(title)

        # security
        self.chk_confirm = QCheckBox("Confirmar exclusão de arquivos")
        layout.addWidget(self.chk_confirm)

        # import behaviour
        self.chk_auto = QCheckBox("Abrir painel de configuração após importação")
        layout.addWidget(self.chk_auto)

        # destination behaviour
        self.chk_use_source = QCheckBox("Usar pasta do arquivo original como destino")
        layout.addWidget(self.chk_use_source)

        # output directory
        layout.addWidget(QLabel("Pasta de saída padrão"))

        dir_row = QHBoxLayout()
        self.edit_dir = QLineEdit()
        self.btn_dir = QPushButton("Selecionar")

        dir_row.addWidget(self.edit_dir)
        dir_row.addWidget(self.btn_dir)

        layout.addLayout(dir_row)

        # output naming
        layout.addWidget(QLabel("Nome do arquivo de saída"))

        self.naming_mode = QComboBox()
        self.naming_mode.addItems([
            "Manter nome original",
            "Adicionar sufixo",
            "Adicionar timestamp"
        ])
        layout.addWidget(self.naming_mode)

        self.edit_suffix = SuffixLineEdit()
        self.edit_suffix.setVisible(False)
        layout.addWidget(self.edit_suffix)

        layout.addWidget(QLabel("Se arquivo já existir"))

        self.collision_mode = QComboBox()
        self.collision_mode.addItems([
            "Adicionar numeração sequencial",
            "Sobrescrever arquivo existente",
            "Cancelar operação"
        ])
        layout.addWidget(self.collision_mode)

        self.preview = QLabel("Resultado: exemplo_video_compactado.mp4\\nSe já existir: exemplo_video_compactado_1.mp4")
        layout.addWidget(self.preview)

        layout.addStretch()

        self._load()
        self._update_state()
        self._update_preview()
        self._update_suffix_state()

        self.chk_use_source.toggled.connect(self._update_state)
        self.btn_dir.clicked.connect(self._select_dir)
        self.naming_mode.currentIndexChanged.connect(self._update_preview)
        self.naming_mode.currentIndexChanged.connect(self._update_suffix_state)
        self.edit_suffix.textChanged.connect(self._update_preview)
        self.collision_mode.currentIndexChanged.connect(self._update_preview)

    
    
    def _apply_field_style(self, widget, enabled: bool):
        if enabled:
            widget.setStyleSheet("QLineEdit { background-color: #1e1e1e; color: #ffffff; }")
        else:
            widget.setStyleSheet("QLineEdit { background-color: #3a3a3a; color: #aaaaaa; }")

    def _update_suffix_state(self):
        mode = self.naming_mode.currentIndex()
        enabled = (mode == 1)
        self.edit_suffix.setEnabled(enabled)
        self.edit_suffix.setVisible(mode == 1)
        self._apply_field_style(self.edit_suffix, enabled)


    
    def _update_preview(self):

        example_name = "exemplo_video.mp4"
        base, ext = example_name.rsplit(".",1)
        ext = "." + ext
        mode = self.naming_mode.currentIndex()

        if mode == 0:
            name = base + ext

        elif mode == 1:
            suffix = self.edit_suffix.text().strip()
            if "|" in suffix:
                suffix = suffix.split("|")[0].strip()
            if suffix and not suffix.startswith("_"):
                suffix = "_" + suffix
            name = base + suffix + ext

        elif mode == 2:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            name = f"{base}_{ts}{ext}"

        if self.collision_mode.currentIndex() == 0:
            seq = name.replace(".mp4", "_1.mp4")
            self.preview.setText(f"Resultado: {name}\nSe já existir: {seq}")
        else:
            self.preview.setText(f"Resultado: {name}")


    def _update_state(self):
        use_source = self.chk_use_source.isChecked()

        if use_source:
            self.edit_dir.setText("Mesma pasta do arquivo original")
            self.edit_dir.setReadOnly(True)
            self.btn_dir.setEnabled(False)
            self._apply_field_style(self.edit_dir, False)
        else:
            cfg = self.service.get()
            path = cfg.output_directory.replace("/", "\\")
            self.edit_dir.setText(path)
            self.edit_dir.setReadOnly(False)
            self.btn_dir.setEnabled(True)
            self._apply_field_style(self.edit_dir, True)

    def _select_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Selecionar pasta de saída")
        if path:
            path = os.path.normpath(path)
            path = path.replace("/", "\\")
            self.edit_dir.setText(path)

    def _load(self):
        cfg = self.service.get()

        self.chk_confirm.setChecked(cfg.confirm_delete)
        self.chk_auto.setChecked(cfg.auto_open_configuration_after_import)
        self.chk_use_source.setChecked(getattr(cfg,"use_source_directory",True))

        path = cfg.output_directory.replace("/", "\\")
        self.edit_dir.setText(path)

    def collect_values(self):

        directory = self.edit_dir.text()

        if self.chk_use_source.isChecked():
            directory = ""
        else:
            directory = os.path.normpath(directory)
            directory = directory.replace("/", "\\")

        return {
            "confirm_delete": self.chk_confirm.isChecked(),
            "auto_open_configuration_after_import": self.chk_auto.isChecked(),
            "use_source_directory": self.chk_use_source.isChecked(),
            "output_directory": directory,
            "output_naming_mode": self.naming_mode.currentIndex(),
            "output_suffix": self.edit_suffix.text(),
            "collision_policy": self.collision_mode.currentIndex()
        }

    def restore_defaults(self):

        defaults = AppConfiguration()

        self.chk_confirm.setChecked(defaults.confirm_delete)
        self.chk_auto.setChecked(defaults.auto_open_configuration_after_import)
        self.chk_use_source.setChecked(defaults.use_source_directory)
        self.edit_dir.setText(defaults.output_directory)

        self.naming_mode.setCurrentIndex(0)
        self.edit_suffix.setText("_compactado")
        self.collision_mode.setCurrentIndex(0)

        self.edit_suffix.restore_default()
        self._update_state()
        self._update_preview()
        self._update_suffix_state()