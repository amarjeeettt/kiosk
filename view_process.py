from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor


class ViewProcessWidget(QWidget):
    print_preview_backbt_clicked = pyqtSignal()

    def __init__(self, parent, title):
        super().__init__(parent)

        self.setup_ui(title)

    def setup_ui(self, title):
        self.title = title

        # Create a layout for the central widget
        layout = QVBoxLayout(self)

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
        
        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(50)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 8)

        
        # Load the image
        self.image = (
            QImage(f"./img/process/test.png")
            .scaledToWidth(1280, Qt.SmoothTransformation)
            .scaledToHeight(int(1280 * (2 / 3)), Qt.SmoothTransformation)
        )
        
        # Apply border radius to the image
        self.apply_border_radius()

        pixmap = QPixmap.fromImage(self.image)
        self.process_image = QLabel()
        self.process_image.setPixmap(pixmap)
        self.process_image.setGraphicsEffect(shadow_effect)
        self.process_image.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.process_image)

    def apply_border_radius(self):
        # Create a mask image with the desired border radius
        mask = QImage(self.image.size(), QImage.Format_ARGB32)
        mask.fill(Qt.transparent)

        # Create a QPainter for the mask
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(QColor(Qt.white)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.image.rect(), 25, 25)
        painter.end()

        # Apply the mask to the image
        self.image.setAlphaChannel(mask)

    def go_back(self):
        self.setVisible(False)
        self.print_preview_backbt_clicked.emit()
