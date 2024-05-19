import glob
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor, QPainterPath


class ProcessButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.border_radius = 35  # Set the desired border radius here

        # Use glob to search for both .png and .jpg files
        image_paths = glob.glob(f"./img/process/{title}.[pj][np]g")
        if image_paths:
            self.image_path = image_paths[0]
            self.pixmap = QPixmap(self.image_path)
        else:
            print(f"Image not found: {title}.png or {title}.jpg")
            self.pixmap = QPixmap()  # Create an empty pixmap if image is not found

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create a rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.border_radius, self.border_radius)

        # Clip the painting region to the rounded rectangle
        painter.setClipPath(path)

        # Draw the pixmap if it's not empty
        if not self.pixmap.isNull():
            painter.drawPixmap(self.rect(), self.pixmap)

        # Draw the button text
        super().paintEvent(event)

    def sizeHint(self):
        if not self.pixmap.isNull():
            return self.pixmap.size()
        else:
            return super().sizeHint()


class MapButton(QPushButton):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)
        self.border_radius = 35  # Set the desired border radius here

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create a rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.border_radius, self.border_radius)

        # Clip the painting region to the rounded rectangle
        painter.setClipPath(path)

        # Draw the pixmap
        painter.drawPixmap(self.rect(), self.pixmap)

        # Draw the button text
        super().paintEvent(event)

    def sizeHint(self):
        return self.pixmap.size()


class ButtonWidget(QWidget):
    process_clicked = pyqtSignal()
    map_clicked = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(parent)

        # Create a layout for the widget
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        process_button = ProcessButton(title, self)
        process_button.setText("View Process")
        process_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                color: #FAFAFA; 
                font-family: Montserrat;
                font-size: 52px;
                font-weight: bold;
                border-radius: 35px;
                letter-spacing: 8px;
                background-color: rgba(0, 0, 0, 75);
            }
            QPushButton:pressed {
                background-color: rgba(124, 47, 62, 85);
            }
        """
        )
        process_button.setFixedSize(840, 380)
        process_button.clicked.connect(self.process)
        layout.addWidget(process_button)

        map_button = MapButton("./img/process/map.jpg", self)
        map_button.setText("View Map")
        map_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                color: #FAFAFA; 
                font-family: Montserrat;
                font-size: 52px;
                font-weight: bold;
                border-radius: 35px;
                letter-spacing: 8px;
                background-color: rgba(0, 0, 0, 75);
            }
            QPushButton:pressed {
                background-color: rgba(124, 47, 62, 85);
            }
        """
        )

        map_button.setFixedSize(840, 380)

        map_button.clicked.connect(self.map)
        layout.addWidget(map_button)

        # Set the layout for the widget
        self.setLayout(layout)

    def process(self):
        self.hide()
        self.process_clicked.emit()

    def map(self):
        self.hide()
        self.map_clicked.emit()


class ProcessWidget(QWidget):
    close_bt_clicked = pyqtSignal()

    def __init__(self, title, parent=None):
        super().__init__(parent)

        # Create a layout for the widget
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignCenter)

        close_bt = QPushButton()
        close_bt.setFixedSize(50, 50)
        close_bt.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/static/error.png'); margin-right: 5px;}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/static/error_pressed.png');}"
        )
        close_bt.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        close_bt.clicked.connect(self.close)

        layout.addWidget(close_bt, alignment=Qt.AlignCenter)

        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(35)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 8)

        self.image_label = QLabel()

        image_paths = glob.glob(f"./img/process/{title}.[pj][np]g")
        if image_paths:
            image_path = image_paths[0]
            self.image = QImage(image_path)
            self.image = self.image.scaledToWidth(1280, Qt.SmoothTransformation)
            self.image = self.image.scaledToHeight(
                int(1280 * (2 / 3)), Qt.SmoothTransformation
            )
        else:
            print(f"Image not found: {title}.png or {title}.jpg")

        self.apply_border_radius()

        pixmap = QPixmap.fromImage(self.image)
        self.image_label.setPixmap(pixmap)
        self.image_label.setGraphicsEffect(shadow_effect)
        self.image_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.image_label)

        # Set the layout for the widget
        self.setLayout(layout)

    def close(self):
        self.hide()
        self.close_bt_clicked.emit()

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


class MapWidget(QWidget):
    close_bt_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a layout for the widget
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignCenter)

        close_bt = QPushButton()
        close_bt.setFixedSize(50, 50)
        close_bt.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/static/error.png'); margin-right: 15px;}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/static/error_pressed.png');}"
        )
        close_bt.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        close_bt.clicked.connect(self.close)

        layout.addWidget(close_bt, alignment=Qt.AlignCenter)

        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(35)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 8)

        self.image_label = QLabel()

        self.image = QImage(f"./img/process/map.jpg").scaled(
            1440, 900, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.apply_border_radius()

        pixmap = QPixmap.fromImage(self.image)
        self.image_label.setPixmap(pixmap)
        self.image_label.setGraphicsEffect(shadow_effect)
        self.image_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.image_label)

        # Set the layout for the widget
        self.setLayout(layout)

    def close(self):
        self.hide()
        self.close_bt_clicked.emit()

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


class ViewProcessWidget(QWidget):
    print_preview_backbt_clicked = pyqtSignal()

    def __init__(self, parent, title):
        super().__init__(parent)

        self.setup_ui(title)

    def setup_ui(self, title):
        self.title = title

        # Create a layout for the central widget
        self.layout = QVBoxLayout(self)

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

        self.layout.addLayout(back_button_layout)

        self.buttons_widget = ButtonWidget(self.title, self)
        self.buttons_widget.process_clicked.connect(self.show_process)
        self.buttons_widget.map_clicked.connect(self.show_map)
        self.layout.addWidget(self.buttons_widget)

    def show_process(self):
        self.process_widget = ProcessWidget(self.title, self)
        self.process_widget.close_bt_clicked.connect(self.go_back_button)
        self.layout.addWidget(self.process_widget)

        self.back_bt.hide()

    def show_map(self):
        self.map_widget = MapWidget(self)
        self.map_widget.close_bt_clicked.connect(self.go_back_button)
        self.layout.addWidget(self.map_widget)

        self.back_bt.hide()

    def go_back_button(self):
        self.buttons_widget.show()
        self.back_bt.show()

    def go_back(self):
        self.setVisible(False)
        self.print_preview_backbt_clicked.emit()
