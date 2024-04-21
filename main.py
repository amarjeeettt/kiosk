import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
)
from PyQt5.QtGui import QFont  # Import QFont for setting font
from PyQt5.QtCore import Qt, QSize
from view_form import ViewFormWindow
from admin_window import AdminScreenWindow


class HomeScreenWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")

        # Set window size
        self.showMaximized()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set background color of the central widget
        central_widget.setStyleSheet("background-color: #A93F55;")

        layout = QVBoxLayout(central_widget)

        # Create first label and add it to the layout
        label = QLabel(
            "Pay-per Print: Lorem ipsum dolor sit amet", alignment=Qt.AlignCenter
        )
        label.setFont(QFont("Montserrat", 64, weight=QFont.Bold))
        label.setWordWrap(True)
        label.setStyleSheet(
            "color: #D8C995; padding-top: 450px; letter-spacing: 4px; "
        )  # Adding stylesheet
        layout.addWidget(
            label, alignment=Qt.AlignVCenter
        )  # Align label vertically center

        # Create second label and add it to the layout
        sub_label = QLabel("Tap anywhere to continue", alignment=Qt.AlignCenter)
        sub_label.setFont(QFont("Roboto", 14, weight=QFont.Bold))
        sub_label.setStyleSheet("color: #F3F7F0; padding-bottom: 320px; ")
        layout.addWidget(
            sub_label, alignment=Qt.AlignVCenter
        )  # Align label vertically center

        admin_bt = QPushButton(self)
        admin_bt.setGeometry(1450, 780, 200, 65)  # (x, y, width, height)
        admin_bt.setIconSize(QSize(65, 65))  # Set the size of the icon
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
        # Close the current window
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

    # Slot to handle going back to the main window
    def go_back_to_home(self):
        # Create an instance of the HomeScreenWindow class and show it
        self.close()
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeScreenWindow()
    window.show()
    sys.exit(app.exec_())
