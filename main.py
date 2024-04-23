import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QDesktopWidget,
)
from PyQt5.QtGui import QFont, QPixmap  
from PyQt5.QtCore import Qt, QSize
from view_form import ViewFormWindow
from admin_window import AdminScreenWindow

class HomeScreenWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.set_background_image()
        self.showMaximized()  # Set window to be maximized

        # Create a central widget to hold the background image
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignVCenter)  # Align the layout vertically

        # Load image for the label
        image_label = QLabel()
        pixmap = QPixmap("./img/logo.png")
        pixmap = pixmap.scaledToWidth(500, Qt.SmoothTransformation)  # Scale the image width to fit the label
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        layout.setContentsMargins(0, 165, 0, 0)

        # Add spacing between image_label and sub_label
        layout.addSpacing(170)

        # Create second label and add it to the layout
        sub_label = QLabel("Touch Anywhere to Continue", alignment=Qt.AlignCenter)
        sub_label.setStyleSheet("color: #A93F55; font-family: Roboto; font-size: 20px; font-weight: bold; letter-spacing: 3px; ")
        layout.addWidget(sub_label)  

        admin_bt = QPushButton(self)
        admin_bt.setGeometry(1380, 765, 200, 65)  
        admin_bt.setIconSize(QSize(65, 65))  
        admin_bt.setFocusPolicy(Qt.NoFocus)
        self.button = admin_bt
        admin_bt.show()

        # Set style sheet to remove background and border
        admin_bt.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/admin_bt.svg');}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/admin_bt_pressed.svg');}"
        )

        # Set up the click event
        admin_bt.clicked.connect(self.show_admin_window)
        central_widget.mousePressEvent = self.switch_window

    def switch_window(self, event):
        self.close()
        self.new_window = ViewFormWindow()
        self.new_window.show()

        # Connect the back button clicked signal from ViewScreenWindow to go_back_to_home slot
        self.new_window.home_screen_backbt_clicked.connect(self.go_back_to_home)

    def show_admin_window(self):
        self.close()
        self.admin_window = AdminScreenWindow()
        self.admin_window.show()

        # Connect the back button clicked signal from AdminScreenWindow to go_back_to_home slot
        self.admin_window.home_screen_backbt_clicked.connect(self.go_back_to_home)
        
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
        background_label.setGeometry(0, 0, screen_resolution.width(), screen_resolution.height())  # Set label size to screen resolution
        background_label.setScaledContents(True)
        

    # Slot to handle going back to the main window
    def go_back_to_home(self):
        self.close()
        self.showMaximized()  # Show maximized window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeScreenWindow()
    window.show()
    sys.exit(app.exec_())
