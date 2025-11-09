import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

class Results(QWidget):
    def __init__(self):
        super().__init__()
        self.results_ui()

    def results_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)

        # title
        title = QLabel("Results")
        title.setStyleSheet("font-weight: 800; font-size: 36px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        # image preview text
        preview_text = QLabel("License Plate Preview")
        preview_text.setContentsMargins(0, 0, 0, 16)
        preview_text.setStyleSheet("font-weight: 800; font-size: 18px;")
        layout.addWidget(preview_text, alignment=Qt.AlignmentFlag.AlignLeft)

        # image preview container
        self.image_label = QLabel()
        self.image_label.setFixedHeight(400)
        self.image_label.setStyleSheet(
            "background: #f5f5f5; border-radius: 12px; padding: 8px;"
        )
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # info row
        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 16, 0, 16)

        # plate box
        plate_box_layout = QVBoxLayout()
        plate_box_layout.setSpacing(0)
        plate_label = QLabel("License Plate Number")
        plate_label.setStyleSheet(
            "font-size: 18px; font-weight: 400;"
        )
        self.plate_text = QLabel("N/A")
        self.plate_text.setStyleSheet(
            "font-size: 36px; font-weight: 800;"
        )
        plate_box_layout.addWidget(plate_label)
        plate_box_layout.addWidget(self.plate_text)

        self.plate_box = QWidget()
        self.plate_box.setLayout(plate_box_layout)
        self.plate_box.setMinimumSize(300, 150)
        self.plate_box.setStyleSheet(
            "padding: 8px; background: #f5f5f5; border-radius: 12px;"
        )

        # status box
        status_box_layout = QVBoxLayout()
        status_box_layout.setSpacing(0)
        status_label = QLabel("Status")
        status_label.setStyleSheet(
            "font-size: 18px; font-weight: 400;"
        )
        self.status_text = QLabel("N/A")
        self.status_text.setStyleSheet(
            "font-size: 36px; font-weight: 800;"
        )
        status_box_layout.addWidget(status_label)
        status_box_layout.addWidget(self.status_text)
        
        self.status_box = QWidget()
        self.status_box.setLayout(status_box_layout)
        self.status_box.setMinimumSize(300, 150)
        self.status_box.setStyleSheet(
            "padding: 8px; font-size: 18px; font-weight: 700; background: #cfe9d9; border-radius: 12px; padding: 8px;"
        )

        info_row.addWidget(self.plate_box)
        info_row.addWidget(self.status_box)

        layout.addLayout(info_row)

    def set_results(self, image_path: str, plate_text: str, status_text: str):
        # set image
        try:
            pix = QPixmap(image_path)
            if not pix.isNull():
                pix = pix.scaledToHeight(140, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(pix)
            else:
                self.image_label.setText("No preview available")
        except Exception:
            self.image_label.setText("No preview available")

        # set plate and status
        self.plate_text.setText(plate_text)
        self.status_text.setText(status_text)