from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class HomeScreenWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Load image for the label
        image_label = QLabel()
        pixmap = QPixmap("./img/logo.png")
        pixmap = pixmap.scaledToWidth(
            500, Qt.SmoothTransformation
        )  # Scale the image width to fit the label
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        layout.setContentsMargins(0, 140, 0, 0)

        # Add spacing between image_label and sub_label
        layout.addSpacing(170)

        # Create second label and add it to the layout
        sub_label = QLabel("Touch Anywhere to Continue", alignment=Qt.AlignCenter)
        sub_label.setStyleSheet(
            "color: #A93F55; font-family: Roboto; font-size: 20px; font-weight: bold; letter-spacing: 3px; "
        )
        layout.addWidget(sub_label)
