import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QRadioButton,
    QTableView,
    QVBoxLayout,
)

from app.models.file_table_model import FileTableModel


AUDIO_EXTENSIONS = (
    ".mp3",
    ".aac",
    ".wav",
    ".flac",
    ".ogg",
    ".m4a",
    ".wma",
    ".opus",
    ".alac",
)


class AssistedImportDialog(QDialog):

    def __init__(self, video_count, audio_count, parent=None, files=None):
        super().__init__(parent)

        self.files = files[:] if files else []

        self.setWindowTitle("Importação Assistida")
        self.resize(620, 540)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        # ---------------- HEADER ----------------
        self.header = QLabel()
        header_row = QHBoxLayout()
        header_row.addWidget(self.header)
        header_row.addStretch()

        self.add_files_btn = QPushButton("Adicionar + arquivos")
        self.remove_btn = QPushButton("Remover selecionado")

        self.add_files_btn.setFixedWidth(150)
        self.remove_btn.setFixedWidth(150)

        header_row.addWidget(self.add_files_btn)
        header_row.addWidget(self.remove_btn)

        layout.addLayout(header_row)

        self.add_files_btn.clicked.connect(self._add_files)

        # ---------------- TABLE ----------------
        self.table = QTableView()
        self.model = FileTableModel(self.files)
        self.table.setModel(self.model)

        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.ExtendedSelection)
        self.table.setSortingEnabled(True)

        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Fixed)

        self.table.setColumnWidth(1, 70)
        self.table.setColumnWidth(2, 70)

        layout.addWidget(self.table)

        # delete shortcut
        self.del_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.table)
        self.del_shortcut.activated.connect(self._remove_selected)

        self.remove_btn.setEnabled(False)

        sel_model = self.table.selectionModel()
        sel_model.selectionChanged.connect(self._on_selection_changed)

        self.remove_btn.clicked.connect(self._remove_selected)

        # ---------------- PANELS ----------------
        panels = QGridLayout()
        layout.addLayout(panels)

        # VIDEO PANEL (sempre criado)
        self.video_box = QGroupBox("Arquivos de vídeo")
        form = QFormLayout(self.video_box)

        self.v_compress = QRadioButton("Compactar vídeo")
        self.v_convert = QRadioButton("Converter vídeo")
        self.v_extract = QRadioButton("Extrair áudio")
        self.v_compress.setChecked(True)

        self.v_mode_video = QComboBox()
        self.v_mode_video.addItems(["Compactar", "Converter", "Extrair áudio"])

        self.v_mode_video.currentIndexChanged.connect(
            lambda i: [
                self.v_compress.setChecked(i == 0),
                self.v_convert.setChecked(i == 1),
                self.v_extract.setChecked(i == 2),
            ]
        )

        vg = QButtonGroup(self)
        vg.addButton(self.v_compress)
        vg.addButton(self.v_convert)
        vg.addButton(self.v_extract)

        self.v_compress.toggled.connect(self._update_output_formats)
        self.v_convert.toggled.connect(self._update_output_formats)
        self.v_extract.toggled.connect(self._update_output_formats)

        form.addRow("Modo do vídeo", self.v_mode_video)

        self.v_container = QComboBox()

        self._video_formats = [
            "MP4",
            "MKV",
            "WEBM",
            "MOV",
            "AVI",
            "FLV",
            "TS",
            "M4V",
        ]

        self._audio_formats = ["MP3", "AAC", "FLAC", "OPUS", "OGG", "WAV", "M4A"]

        self.v_container.addItems(self._video_formats)

        form.addRow("Formato de saída", self.v_container)

        panels.addWidget(self.video_box, 0, 0)

        # AUDIO PANEL (sempre criado)
        self.audio_box = QGroupBox("Arquivos de áudio")
        form = QFormLayout(self.audio_box)

        self.a_convert = QRadioButton("Converter áudio")
        self.a_keep = QRadioButton("Copiar áudio")
        self.a_remove = QRadioButton("Remover áudio")

        self.a_convert.setChecked(True)

        self.v_mode_audio = QComboBox()
        self.v_mode_audio.addItems(["Converter", "Copiar áudio", "Remover"])

        self.v_mode_audio.currentIndexChanged.connect(
            lambda i: [
                self.a_convert.setChecked(i == 0),
                self.a_keep.setChecked(i == 1),
                self.a_remove.setChecked(i == 2),
            ]
        )

        ag = QButtonGroup(self)
        ag.addButton(self.a_convert)
        ag.addButton(self.a_keep)
        ag.addButton(self.a_remove)

        form.addRow("Modo do áudio", self.v_mode_audio)

        self.a_format = QComboBox()
        self.a_format.addItems(["MP3", "AAC", "FLAC", "OPUS", "VORBIS", "WAV"])

        self.a_bitrate = QComboBox()
        self.a_bitrate.addItems(
            ["96 kbps", "128 kbps", "160 kbps", "192 kbps", "256 kbps", "320 kbps"]
        )
        self.a_bitrate.setCurrentText("192 kbps")

        form.addRow("Formato de saída", self.a_format)

        panels.addWidget(self.audio_box, 0, 1)

        # ---------------- FOOTER ----------------
        footer_container = QHBoxLayout()

        self.cancel_btn = QPushButton("Cancelar")
        self.add_btn = QPushButton("Enviar para fila")

        self.cancel_btn.clicked.connect(self.reject)
        self.add_btn.clicked.connect(self._enqueue)

        self.add_files_btn.setFocusPolicy(Qt.NoFocus)
        self.remove_btn.setFocusPolicy(Qt.NoFocus)
        self.cancel_btn.setFocusPolicy(Qt.NoFocus)
        self.add_btn.setFocusPolicy(Qt.NoFocus)

        footer_container.addWidget(self.cancel_btn, 1)
        footer_container.addWidget(self.add_btn, 1)

        panels.addLayout(footer_container, 1, 0, 1, 2)

        self.update_header()

    # ---------------- HEADER UPDATE ----------------

    def update_header(self):
        video = 0
        audio = 0

        for f in self.files:
            ext = os.path.splitext(f)[1].lower()

            if ext in AUDIO_EXTENSIONS:
                audio += 1
            else:
                video += 1

        total = video + audio

        # enable / disable panels dinamicamente
        self.video_box.setEnabled(video > 0)
        self.audio_box.setEnabled(audio > 0)

        audio_label = "áudio" if audio == 1 else "áudios"
        video_label = "vídeo" if video == 1 else "vídeos"
        file_label = "arquivo" if total == 1 else "arquivos"

        self.header.setText(
            f"{total} {file_label}: {video} {video_label} + {audio} {audio_label}"
        )

    # ---------------- SELECTION ----------------

    def _on_selection_changed(self, *args):
        indexes = self.table.selectionModel().selectedRows()
        self.remove_btn.setEnabled(len(indexes) > 0)

    # ---------------- REMOVE ----------------

    def _remove_selected(self):

        rows = sorted(
            [i.row() for i in self.table.selectionModel().selectedRows()],
            reverse=True,
        )

        for r in rows:
            if r < len(self.files):
                self.files.pop(r)

        self.model = FileTableModel(self.files)
        self.table.setModel(self.model)

        sel_model = self.table.selectionModel()
        sel_model.selectionChanged.connect(self._on_selection_changed)

        self.update_header()

    # ---------------- ADD FILES ----------------

    def _add_files(self):

        filters = (
            "Media Files (*.mp4 *.mkv *.webm *.mov *.avi *.flv *.ts "
            "*.mp3 *.aac *.wav *.flac *.opus *.ogg *.m4a)"
        )

        paths, _ = QFileDialog.getOpenFileNames(
            self, "Adicionar arquivos", "", filters
        )

        if not paths:
            return

        added = False

        for p in paths:
            if p not in self.files:
                self.files.append(p)
                added = True

        if not added:
            return

        self.model = FileTableModel(self.files)
        self.table.setModel(self.model)

        sel_model = self.table.selectionModel()
        sel_model.selectionChanged.connect(self._on_selection_changed)

        self.update_header()

    # ---------------- VIDEO FORMAT UPDATE ----------------

    def _update_output_formats(self):

        if self.v_extract.isChecked():
            self.v_container.clear()
            self.v_container.addItems(self._audio_formats)
        else:
            self.v_container.clear()
            self.v_container.addItems(self._video_formats)

    # ---------------- ENQUEUE ----------------

    def _enqueue(self):

        valid_files = []

        for f in self.files:
            try:
                if f and os.path.exists(f):
                    valid_files.append(f)
            except Exception:
                pass

        if not valid_files:
            return

        video_files = []
        audio_files = []

        for f in valid_files:
            ext = os.path.splitext(f)[1].lower()

            if ext in AUDIO_EXTENSIONS:
                audio_files.append(f)
            else:
                video_files.append(f)

        video_mode = None
        video_container = None

        if self.v_compress.isChecked():
            video_mode = "compress"
        elif self.v_convert.isChecked():
            video_mode = "convert"
        elif self.v_extract.isChecked():
            video_mode = "extract"

        video_container = self.v_container.currentText()

        audio_mode = None
        audio_codec = None
        audio_bitrate = None

        if self.a_convert.isChecked():
            audio_mode = "convert"
        elif self.a_keep.isChecked():
            audio_mode = "keep"
        elif self.a_remove.isChecked():
            audio_mode = "remove"

        audio_codec = self.a_format.currentText()
        audio_bitrate = self.a_bitrate.currentText()

        payload = {
            "files": valid_files,
            "video": {
                "mode": video_mode,
                "container": video_container,
            },
            "audio": {
                "mode": audio_mode,
                "codec": audio_codec,
                "bitrate": audio_bitrate,
            },
        }

        self.result_payload = payload
        self.accept()
