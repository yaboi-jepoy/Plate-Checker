import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from pathlib import Path

class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.nav_bar_ui()
        
    def nav_bar_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # title / logo
        self.logo = QLabel()
        # add logo path
        logo_path = Path(__file__).parent / "LPC_logo.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path))
            # set logo size
            pix = pix.scaledToHeight(45, Qt.TransformationMode.SmoothTransformation)
            self.logo.setPixmap(pix)
            self.logo.setFixedHeight(54)
        else:
            # fallback text
            self.logo.setText("License Plate Checker")
            self.logo.setStyleSheet(
                "font-size: 14px;"
            )

        layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)