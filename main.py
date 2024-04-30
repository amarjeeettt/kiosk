import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QDesktopWidget,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from home_screen_widget import HomeScreenWidget
from admin_login import AdminLoginWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.set_background_image()
        self.setWindowTitle("Pay-per Printer")
        self.showFullScreen()

        screen_resolution = app.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.home_screen_widget = HomeScreenWidget(self)
        self.admin_bt = QPushButton("", self)
        
        self.admin_login = AdminLoginWidget(self)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self.centralWidget)
        layout.setAlignment(Qt.AlignCenter)

        # Adding HomeScreenWindow
        layout.addWidget(self.home_screen_widget)
        
        # Adding AdminLoginWindow
        layout.addWidget(self.admin_login)
        self.admin_login.setVisible(False)

        # Set properties of the admin button
        self.admin_bt.setGeometry(1430, 813, 200, 65)
        self.admin_bt.setIconSize(QSize(65, 65))
        self.admin_bt.setFocusPolicy(Qt.NoFocus)
        self.admin_bt.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/admin_bt.svg');}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/admin_bt_pressed.svg');}"
        )
        self.admin_bt.show()
        self.admin_bt.clicked.connect(self.show_admin_login)
    
    def go_back_to_home(self):
        self.home_screen_widget.setVisible(True)
        self.admin_bt.show()
    
    def show_admin_login(self):
        self.home_screen_widget.setVisible(False)
        self.admin_login.show()
        self.admin_bt.hide()
        
        self.admin_login.home_screen_backbt_clicked.connect(self.go_back_to_home)


    def set_background_image(self):
        # Get screen resolution
        screen_resolution = QDesktopWidget().screenGeometry()

        # Load the background image
        pixmap = QPixmap("./img/background.jpg")

        # Resize the background image to fit the screen resolution
        pixmap = pixmap.scaled(screen_resolution.width(), screen_resolution.height())

        # Create a label to display the background image
        background_label = QLabel(self)
        background_label.setPixmap(pixmap)
        background_label.setGeometry(
            0, 0, screen_resolution.width(), screen_resolution.height()
        )  # Set label size to screen resolution
        background_label.setScaledContents(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
