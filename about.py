from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QScrollArea,
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPixmap


class SmoothScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalScrollBar().setSingleStep(15)  # Set the scrolling step size
        self._mousePressPos = None
        self._scrollBarValueAtMousePress = None
        self._animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._animation.setEasingCurve(QEasingCurve.OutQuad)
        self._animation.setDuration(500)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressPos = event.globalPos()
            self._scrollBarValueAtMousePress = self.verticalScrollBar().value()
            self._animation.stop()  # Stop any ongoing animation when the user interacts
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._mousePressPos:
            delta = event.globalPos() - self._mousePressPos
            self.verticalScrollBar().setValue(
                self._scrollBarValueAtMousePress - delta.y()
            )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._mousePressPos:
            delta = event.globalPos() - self._mousePressPos
            target_value = self._scrollBarValueAtMousePress - delta.y()
            self.smoothScrollTo(target_value)
        self._mousePressPos = None
        self._scrollBarValueAtMousePress = None
        super().mouseReleaseEvent(event)

    def smoothScrollTo(self, target_value):
        self._animation.setStartValue(self.verticalScrollBar().value())
        self._animation.setEndValue(target_value)
        self._animation.start()


class AboutWidget(QWidget):
    backbt_clicked = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.image_files = ["./img/about the study.png", "./img/about the authors.png"]

        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        back_button_layout = QHBoxLayout()

        self.back_bt = QPushButton("Back")
        self.back_bt.setFocusPolicy(Qt.NoFocus)
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
                margin-left: 165px;
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

        self.layout.addLayout(back_button_layout)

        scroll_area = SmoothScrollArea(self)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for image_file in self.image_files:
            image_label = QLabel()
            pixmap = QPixmap(image_file)
            image_label.setPixmap(pixmap.scaledToWidth(1480, Qt.SmoothTransformation))
            image_label.setAlignment(Qt.AlignCenter)
            scroll_layout.addWidget(image_label)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        self.layout.addWidget(scroll_area)

    def go_back_button(self):
        self.buttons_widget.show()
        self.back_bt.show()

    def go_back(self):
        self.setVisible(False)
        self.backbt_clicked.emit()
