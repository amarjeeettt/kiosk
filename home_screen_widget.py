from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QLabel,
    QPushButton,
)
from PyQt5.QtCore import Qt, QTimer, QEvent, pyqtSignal
from PyQt5.QtGui import QMovie, QPixmap


class UpperButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()

        pixmap = QPixmap("./img/static/start_img.png")
        scaled_pixmap = pixmap.scaled(
            45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label = QLabel()
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("margin-left: 65px;")

        self.label = QLabel(title)
        self.label.setStyleSheet(
            """
            font-family: Montserrat; 
            font-size: 28px;
            font-weight: bold;
            margin-right: 115px;
            color: #FAEBD7;
            """
        )

        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setFocusPolicy(Qt.NoFocus)
        self.setLayout(layout)


class BottomButton(QPushButton):
    def __init__(self, title, image_path, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            35, 35, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label = QLabel()
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("margin-top: 15px;")

        self.label = QLabel(title)
        self.label.setStyleSheet(
            """
            font-family: Montserrat; 
            font-size: 14px;
            font-weight: bold;
            color: #FAEBD7;
            """
        )

        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setFocusPolicy(Qt.NoFocus)
        self.setLayout(layout)


class HomeScreenWidget(QWidget):
    start_button_clicked = pyqtSignal()
    about_button_clicked = pyqtSignal()
    admin_button_clicked = pyqtSignal()
    go_back_clicked = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(25000)
        self.inactivity_timer.timeout.connect(self.go_back)
        self.inactivity_timer.start()

        self.installEventFilter(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Load image for the label
        image_label = QLabel()
        movie = QMovie("./img/logo.gif")
        image_label.setMovie(movie)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        layout.setContentsMargins(0, 35, 0, 0)
        movie.start()

        button_layouts = QVBoxLayout()

        start_button = UpperButton("START")
        start_button.setFixedSize(405, 95)
        start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border-radius: 15px;
            }
            QPushButton::pressed {
                background-color: #19323C;
            }
            """
        )
        start_button.setFocusPolicy(Qt.NoFocus)
        start_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        start_button.clicked.connect(self.go_to_forms)

        bottom_buttons = QHBoxLayout()
        bottom_buttons.setAlignment(Qt.AlignCenter)

        about_button = BottomButton("ABOUT", "./img/static/about_img.png")
        about_button.setFixedSize(198, 115)
        about_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border-radius: 15px;
            }
            QPushButton::pressed {
                background-color: #19323C;
            }
            """
        )
        about_button.setFocusPolicy(Qt.NoFocus)
        about_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        about_button.clicked.connect(self.go_to_about)

        admin_button = BottomButton("ADMIN", "./img/static/admin_img.png")
        admin_button.setFixedSize(198, 115)
        admin_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border-radius: 15px;
            }
            QPushButton::pressed {
                background-color: #19323C;
            }
            """
        )
        admin_button.setFocusPolicy(Qt.NoFocus)
        admin_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        admin_button.clicked.connect(self.go_to_admin)

        bottom_buttons.addWidget(about_button)
        bottom_buttons.addWidget(admin_button)

        button_layouts.addWidget(start_button, alignment=Qt.AlignCenter)
        button_layouts.addLayout(bottom_buttons)

        layout.addLayout(button_layouts)

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.KeyPress]:
            self.reset_inactivity_timer()
        return super(HomeScreenWidget, self).eventFilter(obj, event)

    def reset_inactivity_timer(self):
        if self.inactivity_timer.isActive():
            self.inactivity_timer.stop()
        self.inactivity_timer.start()

    def go_back(self):
        self.inactivity_timer.stop()
        self.setVisible(False)
        self.go_back_clicked.emit()

    def go_to_forms(self):
        self.inactivity_timer.stop()
        self.setVisible(False)
        self.start_button_clicked.emit()

    def go_to_about(self):
        self.inactivity_timer.stop()
        self.setVisible(False)
        self.about_button_clicked.emit()

    def go_to_admin(self):
        self.inactivity_timer.stop()
        self.setVisible(False)
        self.admin_button_clicked.emit()
