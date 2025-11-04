from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt

class FileDrop(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.file_drop_ui()

    def file_drop_ui(self):
        # layout
        file_drop_layout = QVBoxLayout()
        # label
        self.label = QLabel("Drag and drop files here", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            """
                font-size: 18px;
                padding: 200px;
            """
        )
        file_drop_layout.addWidget(self.label)

        # container widget
        self.container = QWidget()
        self.setLayout(file_drop_layout)
        # main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)
        self.setStyleSheet(
            """
                border-width: 2px;
                border-style: dashed;
                border-radius: 15px;
                background-color: #D9D9D9;
            """
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
            self.label.setText("\n".join(file_paths))
        else:
            event.ignore()