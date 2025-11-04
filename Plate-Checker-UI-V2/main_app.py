import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

# add files
from top_bar import TopBar
from home import Home

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("License Plate Checker - Group 4")
        # set minimum size
        self.setMinimumSize(1200, 800)
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(0)

        # call functions
        self.top_bar = TopBar()
        self.home = Home()

        # add widgets/layouts
        layout.addWidget(self.top_bar)
        layout.addWidget(self.home)