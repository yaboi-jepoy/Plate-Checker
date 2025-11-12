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
        preview_text.setStyleSheet("font-size: 18px;")
        layout.addWidget(preview_text, alignment=Qt.AlignmentFlag.AlignLeft)

        # image preview container
        self.image_label = QLabel()
        self.image_label.setFixedHeight(600)
        self.image_label.setStyleSheet(
            "background: #f5f5f5; border-radius: 12px;"
        )
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # info row
        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 16, 0, 16)

        # plate box
        plate_box_layout = QVBoxLayout()
        plate_box_layout.setSpacing(4)
        plate_box_layout.setContentsMargins(20, 20, 20, 20)
        plate_box_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        plate_label = QLabel("License Plate Number")
        plate_label.setStyleSheet(
            "font-size: 18px;"
        )
        self.plate_text = QLabel("N/A")
        self.plate_text.setStyleSheet(
            "font-size: 36px; font-weight: 800;"
        )
        plate_box_layout.addWidget(plate_label)
        plate_box_layout.addWidget(self.plate_text)

        self.plate_box = QWidget()
        self.plate_box.setLayout(plate_box_layout)
        self.plate_box.setMinimumSize(300, 100)
        self.plate_box.setStyleSheet(
            "background: #f5f5f5; border-radius: 12px;"
        )

        # status box styling
        self.status_box_styling = "font-size: 18px; background: #f5f5f5; border-radius: 12px;"

        # status box
        status_box_layout = QVBoxLayout()
        status_box_layout.setSpacing(4)
        status_box_layout.setContentsMargins(20, 20, 20, 20)
        status_box_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        status_label = QLabel("Status")
        status_label.setStyleSheet(
            "font-size: 18px;"
        )
        self.status_text = QLabel("N/A")
        self.status_text.setStyleSheet(
            "font-size: 36px; font-weight: 800;"
        )
        status_box_layout.addWidget(status_label)
        status_box_layout.addWidget(self.status_text)
        
        self.status_box = QWidget()
        self.status_box.setLayout(status_box_layout)
        self.status_box.setMinimumSize(300, 100)

        info_row.addWidget(self.plate_box)
        info_row.addWidget(self.status_box)

        layout.addLayout(info_row)

        # plate details section
        self.details_container = QWidget()
        self.details_container.setStyleSheet("background: #f5f5f5; border-radius: 12px;")
        details_layout = QVBoxLayout(self.details_container)
        details_layout.setContentsMargins(20, 20, 20, 20)
        details_layout.setSpacing(4)

        # details title
        details_title = QLabel("Vehicle Details")
        details_title.setStyleSheet("font-size: 18px; color: black;")
        details_title.setContentsMargins(0, 0, 0, 16)
        details_layout.addWidget(details_title)

        # details grid
        self.details_grid = QGridLayout()

        # create detail labels
        self.mv_classification_label = self.create_detail_row("MV Classification:", "N/A")
        self.lto_office_label = self.create_detail_row("LTO NRU Office:", "N/A")
        self.released_to_label = self.create_detail_row("Released To:", "N/A")
        self.date_released_label = self.create_detail_row("Date Released:", "N/A")

        details_layout.addLayout(self.details_grid)
        self.details_container.hide()

        layout.addWidget(self.details_container)

        # reset button
        self.reset_btn = QPushButton("Check Another Plate")
        self.reset_btn.setMinimumSize(250, 48)
        self.reset_btn.setStyleSheet(
            """
                QPushButton { 
                    padding: 12px 18px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    color: white;
                    background-color: #42A5F5;
                    margin-top: 16px;
                }
                QPushButton:hover {
                    background-color: #1E88E5;
                }
            """
        )
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.reset_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def create_detail_row(self, label_text: str, value: str) -> QLabel:
        row = self.details_grid.rowCount()
        
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 18px; color: black;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-weight: 800; font-size: 18px; color: black;")
        value_label.setWordWrap(True)
        
        self.details_grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignTop)
        self.details_grid.addWidget(value_label, row, 1)
        
        return value_label

    def set_results(self, image_path: str, plate_text: str, status_text: str, status_color: str, plate_details: dict = None):
        # set image
        try:
            pix = QPixmap(image_path)
            if not pix.isNull():
                pix = pix.scaledToHeight(580, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(pix)
            else:
                self.image_label.setText("No preview available")
        except Exception:
            self.image_label.setText("No preview available")

        # set plate and status
        self.plate_text.setText(plate_text)
        self.status_text.setText(status_text)
        self.status_box.setStyleSheet(self.status_box_styling + status_color)

        # display plate details if provided and registered
        if plate_details and status_text == "Registered":
            self.mv_classification_label.setText(plate_details.get('mv_classification', 'N/A'))
            self.lto_office_label.setText(plate_details.get('lto_nru_office', 'N/A'))
            self.released_to_label.setText(plate_details.get('released_to', 'N/A'))
            self.date_released_label.setText(plate_details.get('date_released', 'N/A'))
            self.details_container.show()
        else:
            self.details_container.hide()