from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap


class ViewProcessWidget(QWidget):
    print_preview_backbt_clicked = pyqtSignal()

    def __init__(self, parent, title):
        super().__init__(parent)

        self.setup_ui(title)

    def setup_ui(self, title):
        self.title = title
        print(self.title)

        # Create a layout for the central widget
        layout = QVBoxLayout(self)

        # Create a label to display some text in the window
        label = QLabel(self.title)
        label.setAlignment(Qt.AlignCenter)  # Align text to the center

        # Add back button to the layout
        back_button_layout = QHBoxLayout()
        self.back_bt = QPushButton("Back")
        self.back_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E; 
                color: #FAEBD7; 
                font-family: Montserrat;
                font-size: 16px; 
                font-weight: bold; 
                border-radius: 10px;
                border: none;
                margin-left: 35px;
                min-width: 150px;
                min-height: 80px;
                margin-top: 35px;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        self.back_bt.setFocusPolicy(Qt.NoFocus)
        self.back_bt.clicked.connect(self.go_back)
        back_button_layout.addWidget(self.back_bt, alignment=Qt.AlignLeft)
        layout.addLayout(back_button_layout)

        layout.addWidget(label)

    def go_back(self):
        self.setVisible(False)
        self.print_preview_backbt_clicked.emit()
