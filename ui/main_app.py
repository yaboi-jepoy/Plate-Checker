import sys, os
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer

# add files
from sections.home import Home
from sections.results import Results
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import plate_detect
import checkPlate

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("License Plate Checker - Group 4")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet( "background-color: #ECEFF1; color: black;")
        self.setup_menu_bar()
        self.setup_ui()
    
    def setup_menu_bar(self):
        menubar = self.menuBar()
        options_menu = menubar.addMenu("Options")
        
        reset_action = QAction("Reset", self)
        reset_action.setShortcut("Ctrl+R")
        reset_action.setStatusTip("Reset application")
        reset_action.triggered.connect(self.reset_application)
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        
        options_menu.addAction(reset_action)
        options_menu.addAction(exit_action)
    
    def setup_ui(self):
        # central area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        self.setCentralWidget(scroll)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(16)

        # call sections
        self.home = Home()

        self.results = Results()
        self.results.hide()

        # add sections to layout
        layout.addWidget(self.home)
        layout.addWidget(self.results)

        # connect proceed button
        try:
            self.home.proceed.connect(self.home_proceed)
        except Exception:
            pass

        # connect reset button
        try:
            self.results.reset_btn.clicked.connect(self.reset_application)
        except Exception:
            pass

        self._scroll_area = scroll

    def home_proceed(self, files: list):
        image_path = files[0] if files else None
        plate_text = "N/A"
        status_text = "Unknown"
        status_color = "background-color: #f5f5f5;"
        plate_details = None
        
        if image_path:
            try:
                template_dir = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 
                    "templates"
                )
                # Run plate detection function
                recognized_text = plate_detect.recognize_license_plate(
                    image_path, 
                    template_directory=template_dir
                )
                # Check recognition
                if recognized_text and not recognized_text.startswith("License plate") and not recognized_text.startswith("Failed") and not recognized_text.startswith("No characters"):
                    plate_text = recognized_text
                    # Check plate registration from LTO website
                    try:
                        print(f"Checking plate registration for: {plate_text}")
                        results, plate_details = checkPlate.check_plate(plate_text)
                        # Verify if plate is actually registered
                        if plate_details and any(plate_details.values()):
                            status_text = "Registered"
                            status_color = "background-color: #66BB6A;" # Green
                        else:
                            status_text = "Not Registered"
                            status_color = "background-color: #FFCA28;" # Yellow/Orange
                            plate_details = None
                    except Exception as e:
                        print(f"Error checking plate registration: {e}")
                        status_text = "Detected (Verification Failed)"
                        status_color = "background-color: #FFCA28;" # Yellow/Orange
                        plate_details = None
                else:
                    plate_text = "Invalid"
                    status_text = "Failed"
                    status_color = "background-color: #EF5350;" # Red
                    
            except Exception as e:
                print(f"Error during plate recognition: {e}")
                plate_text = "Error"
                status_text = "Failed"
                status_color = "background-color: #EF5350;" # Red

        try:
            self.results.set_results(image_path or "", plate_text, status_text, status_color, plate_details)
            self.results.show()
            # Scroll down to results
            QTimer.singleShot(100, lambda: self._scroll_area.verticalScrollBar().setValue(
                self._scroll_area.verticalScrollBar().maximum()
            ))
        except Exception as e:
            print(f"Error displaying results: {e}")
    
    def reset_application(self):
        """Reset the application to initial state"""
        try:
            # Clear the file drop widget
            self.home.on_clear()
            # Hide results section
            self.results.hide()
            # Scroll up to top
            QTimer.singleShot(100, lambda: self._scroll_area.verticalScrollBar().setValue(0))
            
        except Exception as e:
            print(f"Error during reset: {e}")