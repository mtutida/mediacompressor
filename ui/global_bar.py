from PySide6.QtCore import QPoint, QSize
from PySide6.QtGui import QIcon

from PySide6.QtWidgets import QMenu, QApplication, QToolButton, QFrame, QHBoxLayout, QPushButton, QFileDialog, QSizePolicy
from PySide6.QtCore import QSettings
from interaction_model.event_bridge import event_bridge
from types import SimpleNamespace
import os, threading
from engine.ffprobe_probe import probe
from engine.thumbnail_generator import generate_thumbnail
from ui.assisted_import_dialog import AssistedImportDialog

import tempfile

BTN_WIDTH = None
VIDEO_EXT = (".mp4",".mkv",".avi",".mov",".webm")
AUDIO_EXT = (".mp3",".aac",".wav",".flac",".ogg",".m4a",".wma",".opus",".alac")

class GlobalBarWidget(QFrame):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("GlobalBarWidget")

        self.settings = QSettings("MediaCompressor","MediaCompressor")
        self._last_import_dir = self.settings.value("last_import_dir", os.path.expanduser("~"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4,4,4,4)
        layout.setSpacing(3)

        self.btn_add = QPushButton("Adicionar")
        self.btn_add.setToolTip("Adiciona arquivos em modo assistido")
        self.btn_add.setToolTipDuration(5000)
        self.btn_add.setMouseTracking(True)
        self.btn_add_quick = QPushButton("Adicionar Rápido")
        self.btn_add_quick.setToolTip("Adiciona arquivos em modo simples")
        self.btn_import_folder = QPushButton("Importar Pasta")
        self.btn_select_all = QPushButton("Selecionar Tudo")

        for b in [self.btn_add,self.btn_add_quick,self.btn_import_folder,self.btn_select_all]:
            b.setMinimumWidth(110)
            b.setMinimumHeight(34)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_add_quick)
        layout.addWidget(self.btn_import_folder)
        layout.addWidget(self.btn_select_all)
        

        self.menu_button = QToolButton()
        self.menu_button.setCheckable(True)
        self.menu_button.setText("")
        self.menu_button.setIcon(QIcon("ui/icons/vertical_dots.svg"))
        self.menu_button.setIconSize(QSize(18,18))
        self.menu_button.setAutoRaise(True)
        self.menu_button.setFixedSize(36, 30)
        from PySide6.QtGui import QFont
        font = self.menu_button.font()
        font.setPointSize(20)
        font.setWeight(QFont.Weight.DemiBold)
        self.menu_button.setFont(font)
        self.menu_button.setStyleSheet("""
QToolButton {
    background: transparent;
    border-radius: 6px;
    border: 1px solid transparent;
}
QToolButton:hover {
    border: 1px solid rgba(255,255,255,0.45);
}

QToolButton:checked {
    background: rgba(255,255,255,0.14);
}

QToolButton:hover {
    border: 1px solid rgba(255,255,255,0.45);
}
""")
        self.menu_button.clicked.connect(self._open_menu)
        layout.addWidget(self.menu_button)

        self.setLayout(layout)

        self.btn_add.clicked.connect(self._open_single_dialog)
        self.btn_add_quick.clicked.connect(self._open_multi_dialog)
        self.btn_import_folder.clicked.connect(self._import_folder)
        self.btn_select_all.clicked.connect(self._select_all)

    
    def _open_single_dialog(self):
        files,_ = QFileDialog.getOpenFileNames(self,"Selecionar arquivos",self._last_import_dir,"All Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.wmv *.m4v *.ts *.mts *.m2ts *.3gp *.mpg *.mpeg *.vob);;All Audio Files (*.mp3 *.aac *.wav *.flac *.ogg *.m4a *.wma *.opus *.alac);;All Files (*.*)")
        if not files:
            return

        self._last_import_dir = os.path.dirname(files[0])
        self.settings.setValue("last_import_dir", self._last_import_dir)

        video_count = 0
        audio_count = 0

        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in AUDIO_EXT:
                audio_count += 1
            else:
                video_count += 1

        dlg = AssistedImportDialog(video_count,audio_count,self,files=files)
        from PySide6.QtWidgets import QDialog
        if dlg.exec() != QDialog.Accepted:
            return

        for p in files:
            self._create_job(p)


    def _open_multi_dialog(self):
        files,_ = QFileDialog.getOpenFileNames(self,"Adicionar arquivos diretamente",self._last_import_dir,"All Video Files (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.wmv *.m4v *.ts *.mts *.m2ts *.3gp *.mpg *.mpeg *.vob);;All Audio Files (*.mp3 *.aac *.wav *.flac *.ogg *.m4a *.wma *.opus *.alac);;All Files (*.*)")
        if files:
            self._last_import_dir = os.path.dirname(files[0])
            self.settings.setValue("last_import_dir", self._last_import_dir)
        for p in files:
            self._create_job(p)

    def _import_folder(self):
        folder = QFileDialog.getExistingDirectory(self,"Selecionar pasta", self._last_import_dir)
        if not folder: return
        self._last_import_dir = folder
        self.settings.setValue("last_import_dir", self._last_import_dir)
        for root,_,files in os.walk(folder):
            for f in files:
                if f.lower().endswith(VIDEO_EXT + AUDIO_EXT):
                    self._create_job(os.path.join(root,f))

    
    def _create_job(self,path):
        name=os.path.basename(path)

        

        # validation before import
        try:
            result = probe(path)
            if result is None:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Arquivo inválido", f"O arquivo '{os.path.basename(path)}' não pôde ser importado.")
                return
            codec,res,fps,duration,container = result
        except Exception:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Erro ao analisar arquivo", f"Falha ao analisar '{os.path.basename(path)}'.")
            return


        job = SimpleNamespace(
            file_name=name,
            status="ANALYZING",
            progress=0,
            codec="?",
            resolution="?",
            source_path=path
        )

        event_bridge.emit("job_enqueued",{"job":job})

        threading.Thread(target=self._probe_metadata,args=(job,),daemon=True).start()


    def _probe_metadata(self,job):
        codec,res,fps,duration,container = probe(job.source_path)

        job.codec = codec
        job.resolution = res
        job.fps = fps
        job.duration = duration
        job.container = container

        event_bridge.emit("job_updated",{"job":job})

        threading.Thread(target=self._generate_thumbnail,args=(job,),daemon=True).start()

    def _generate_thumbnail(self,job):
        thumb=None
        try:
            tmp=tempfile.gettempdir()
            out=os.path.join(tmp,job.file_name+'.jpg')
            thumb=generate_thumbnail(job.source_path,out)
        except Exception:
            thumb=None

        job.thumbnail = thumb
        job.status = "READY"
        event_bridge.emit("job_updated",{"job":job})

    def _open_menu(self):
        menu = QMenu(self)

        # safer menu font sizing
        font = menu.font()
        size = font.pointSize()
        if size <= 0:
            size = 10
        font.setPointSize(size + 1)
        menu.setFont(font)

        act_prefs = menu.addAction("Preferências")
        menu.addSeparator()
        act_help = menu.addAction("Ajuda")
        act_about = menu.addAction("Sobre")
        menu.addSeparator()
        act_exit = menu.addAction("Sair")

        from PySide6.QtGui import QCursor
        action = menu.exec(QCursor.pos())

        parent = self.window()

        if action == act_prefs and hasattr(parent,"open_configuration"):
            parent.open_configuration()

        elif action == act_help:
            print("Ajuda selecionada")


        elif action == act_about:
            from PySide6.QtWidgets import QMessageBox
            try:
                from core.app_version import APP_VERSION
            except Exception:
                APP_VERSION = "Unknown"

            QMessageBox.information(
                self,
                "Sobre MediaCompressor",
                "MediaCompressor\n\nVersão: " + str(APP_VERSION) + "\n\nAutor: Marcelo Tutida\nPython • FFmpeg\n\n(Projeto experimental de aprendizado\ncom auxílio de IA)"
            )

        elif action == act_exit:
            QApplication.quit()

    def _select_all(self):
        parent = self.window()
        if hasattr(parent, "file_list"):
            parent.file_list.selectAll()
