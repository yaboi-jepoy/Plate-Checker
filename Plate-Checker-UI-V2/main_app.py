import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer

# add files
from sections.home import Home
from sections.results import Results

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("License Plate Checker - Group 4")
        # set minimum size
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(
            "background-color: #ffffff;"
            "color: #000000;"
        )
        self.setup_ui()
    
    def setup_ui(self):
        # scrollable central area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        self.setCentralWidget(scroll)

        layout = QVBoxLayout(container)
        layout.setSpacing(20)

        # widgets
        self.home = Home()
        self.results = Results()

        # hide results initially
        self.results.hide()

        # add widgets to layout
        layout.addWidget(self.home)
        layout.addWidget(self.results)

        # connect home proceed signal
        try:
            self.home.proceed.connect(self.on_home_proceed)
        except Exception:
            pass

        self._scroll_area = scroll

    def on_home_proceed(self, files: list):
        image_path = files[0] if files else None
        plate_text = "N/A"
        if image_path:
            import os
            plate_text = os.path.splitext(os.path.basename(image_path))[0].replace('_', ' ').upper()

        status_text = "Registered"

        try:
            self.results.set_results(image_path or "", plate_text, status_text)
            self.results.show()
            QTimer.singleShot(100, lambda: self._scroll_area.verticalScrollBar().setValue(self._scroll_area.verticalScrollBar().maximum()))
        except Exception:
            pass