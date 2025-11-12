import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal

from widgets.file_drop import FileDrop

class Home(QWidget):
    def __init__(self):
        super().__init__()
        self.home_ui()

    # emit when user clicks proceed with files list
    proceed = pyqtSignal(list)

    def home_ui(self):
        # home layout
        home_layout = QVBoxLayout()
        home_layout.setContentsMargins(40, 40, 40, 40)
        home_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(home_layout)

        # title
        self.title = QLabel("License Plate Checker")
        self.title.setStyleSheet(
            """
                font-weight: 800;
                font-size: 36px;
            """
        )
        # subtext
        self.subtext = QLabel("Verify your vehicle’s plate number and registration.")
        self.subtext.setStyleSheet(
            """
                font-size: 14px;
                color: #333333;
            """
        )
        
        # upload button
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 16, 0, 0)
        buttons_layout.setSpacing(12)

        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.setMinimumSize(250, 48)
        self.upload_btn.setStyleSheet(
            """
                QPushButton { 
                    padding: 12px 18px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    color: white;
                    background-color: #42A5F5;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1E88E5;
                }
            """
        )
        self.upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # clear button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setMinimumSize(250, 48)
        self.clear_btn.setStyleSheet(
            """
                QPushButton { 
                    padding: 12px 18px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    color: white;
                    background-color: #EF5350;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #E53935;
                }
            """
        )
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        buttons_layout.addWidget(self.upload_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        buttons_layout.addWidget(self.clear_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # file drop widget
        self.file_drop_widget = FileDrop()

        try:
            self.file_drop_widget.files_changed.connect(self.on_files_changed)
        except Exception:
            pass

        # proceed button
        self.proceed_btn = QPushButton("Proceed")
        self.proceed_btn.setContentsMargins(0, 16, 0, 0)
        self.proceed_btn.setStyleSheet(
            """
                QPushButton { 
                    padding: 12px 18px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    color: white;
                    background-color: #66BB6A;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #43A047;
                }
            """
        )
        self.proceed_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.proceed_btn.setMinimumSize(250, 48)

        # connect button events
        self.upload_btn.clicked.connect(self.on_upload)
        self.clear_btn.clicked.connect(self.on_clear)
        self.proceed_btn.clicked.connect(self.on_proceed)

        # add widgets to layout
        home_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        home_layout.addWidget(self.subtext, alignment=Qt.AlignmentFlag.AlignCenter)
        home_layout.addLayout(buttons_layout)
        home_layout.addWidget(self.file_drop_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        home_layout.addWidget(self.proceed_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_upload(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "Images (*.png *.jpg *.jpeg);;All Files (*)")
        if path:
            try:
                self.file_drop_widget.set_files([path])
            except Exception:
                try:
                    self.file_drop_widget.label.setText(path)
                except Exception:
                    pass

    def on_clear(self):
        try:
            self.file_drop_widget.clear_files()
        except Exception:
            try:
                self.file_drop_widget.label.setText("Drag and drop files here")
            except Exception:
                pass

    def on_files_changed(self, files: list):
        self.proceed_btn.setEnabled(bool(files))

    def on_proceed(self):
        files = []
        try:
            files = getattr(self.file_drop_widget, 'files', []) or []
        except Exception:
            files = []
        if not files:
            QMessageBox.information(self, "No files", "Please add a file before proceeding.")
            return
        
        try:
            self.proceed.emit(files)
        except Exception:
            QMessageBox.information(self, "Proceeding", f"Proceeding with {len(files)} file(s):\n{files[0]}")