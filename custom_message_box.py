from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal


class CustomMessageBox(QDialog):
    # Signal emitted when the OK button is clicked
    ok_button_clicked = pyqtSignal()

    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #EBEBEB;")  # Set background color

        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 24px; font-family: Montserrat; font-weight: bold; color: #7C2F3E;"
        )  # Title label styling
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Spacer item for layout spacing
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)  # Allow message to wrap if too long
        message_label.setStyleSheet("font-size: 16px; font-family: Roboto; ")
        layout.addWidget(message_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Spacer item for layout spacing
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFocusPolicy(Qt.NoFocus)
        ok_button.setFixedSize(125, 45)
        ok_button.clicked.connect(self.on_ok_button_clicked)
        ok_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;  /* Button color */
                border-radius: 5px;
                color: #FAEBD7;  /* Text color */
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:pressed {
                background-color: #D8973C;  /* Button color when pressed */
            }
            """
        )
        button_layout.addWidget(ok_button, alignment=Qt.AlignCenter)

    def on_ok_button_clicked(self):
        # Emit the signal when OK button is clicked and close the dialog
        self.ok_button_clicked.emit()
        self.accept()
