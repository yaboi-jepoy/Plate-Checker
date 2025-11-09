from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, pyqtSignal

class FileDrop(QWidget):
    
    files_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.files = []
        self.file_drop_ui()

    def file_drop_ui(self):
        self.setStyleSheet(
            """
                border-width: 2px;
                border-style: dashed;
                border-radius: 15px;
                background-color: #D9D9D9;
            """
        )
        self.setFixedSize(820, 420)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        main_layout = QVBoxLayout(self)

        # label
        self.label = QLabel("Drag and drop files here", self)
        self.label.setFixedSize(700, 400)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            """
                font-size: 18px;
            """
        )
        main_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.set_files(file_paths)
        else:
            event.ignore()

    def set_files(self, file_paths: list):
        if not file_paths:
            self.clear_files()
            return
        self.files = file_paths
        display = "\n".join([str(p) for p in self.files])
        self.label.setText(display)
        try:
            self.files_changed.emit(self.files)
        except Exception:
            pass

    def clear_files(self):
        self.files = []
        self.label.setText("Drag and drop files here.")
        try:
            self.files_changed.emit(self.files)
        except Exception:
            pass