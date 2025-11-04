import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

from file_drop import FileDrop

class Home(QWidget):
    def __init__(self):
        super().__init__()
        self.home_ui()

    def home_ui(self):
        # layout
        home_layout = QVBoxLayout()
        home_layout.addStretch()
        self.setLayout(home_layout)

        # title
        self.title = QLabel("License Plate Checker")
        self.title.setStyleSheet(
            """
                font-weight: bold;
                font-size: 24px;
            """
        )
        # subtext
        self.subtext = QLabel("Verify your vehicle’s plate number and registration.") # change to a more concise function description
        self.subtext.setStyleSheet(
            """
                font-size: 18px;
            """
        )

        # button styling
        button_styling = """
            padding: 8px 14px;
            font-size: 16px;
            font-weight: bold;
        """

        # upload and clear button
        buttons_layout = QHBoxLayout()

        self.upload_btn = QPushButton("Upload File")
        self.upload_btn.setMinimumSize(250,50)
        self.upload_btn.setStyleSheet(button_styling + "background-color: blue;")

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setMinimumSize(250,50)
        self.clear_btn.setStyleSheet(button_styling + "background-color: red;")

        buttons_layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        buttons_layout.addWidget(self.clear_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # file drop widget
        self.file_drop_widget = FileDrop()

        # proceed button
        self.proceed_btn = QPushButton("Proceed")
        self.proceed_btn.setStyleSheet(button_styling)
        self.proceed_btn.setMinimumSize(250,50)

        # add widgets to layout
        home_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        home_layout.addWidget(self.subtext, alignment=Qt.AlignmentFlag.AlignCenter)
        home_layout.addLayout(buttons_layout)
        home_layout.addWidget(self.file_drop_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        home_layout.addWidget(self.proceed_btn, alignment=Qt.AlignmentFlag.AlignCenter)