from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMovie


class HomeScreenWidget(QWidget):
    start_button_clicked = pyqtSignal()
    about_button_clicked = pyqtSignal()
    admin_button_clicked = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Load image for the label
        image_label = QLabel()
        movie = QMovie("./img/logo.gif")
        image_label.setMovie(movie)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        layout.setContentsMargins(0, 80, 0, 0)

        movie.start()

        # Add spacing between image_label and sub_label
        layout.addSpacing(80)

        button_layouts = QVBoxLayout()

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.go_to_forms)

        bottom_buttons = QHBoxLayout()

        about_button = QPushButton("About")
        about_button.setEnabled(False)
        about_button.clicked.connect(self.go_to_about)

        admin_button = QPushButton("Admin")
        admin_button.clicked.connect(self.go_to_admin)

        bottom_buttons.addWidget(about_button)
        bottom_buttons.addWidget(admin_button)

        button_layouts.addWidget(start_button)
        button_layouts.addLayout(bottom_buttons)

        layout.addLayout(button_layouts)

    def go_to_forms(self):
        self.setVisible(False)
        self.start_button_clicked.emit()

    def go_to_about(self):
        self.setVisible(False)
        self.about_button_clicked.emit()

    def go_to_admin(self):
        self.setVisible(False)
        self.admin_button_clicked.emit()
