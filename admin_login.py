import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QLabel,
    QDesktopWidget,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from admin_window import AdminScreenWindow


class AdminLoginWindow(QMainWindow):
    home_screen_backbt_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.set_background_image()
        self.showMaximized()
        
        # Connect database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT admin_password FROM kiosk_settings LIMIT 1")
        self.admin_password = cursor.fetchone()[0]

        conn.close()

        # Create central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a white background square layout
        self.square_layout = QWidget()
        self.square_layout.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 20px;"
        )  # Updated styling
        self.square_layout.setContentsMargins(50, 0, 50, 0)
        self.square_layout.setFixedSize(800, 800)

        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(50)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 12)

        # Apply the shadow effect to the square_frame
        self.square_layout.setGraphicsEffect(shadow_effect)

        # Create widgets
        self.input_edit = QLineEdit()
        self.input_edit.setAlignment(Qt.AlignCenter)
        self.input_edit.setEchoMode(QLineEdit.Password)
        self.input_edit.setStyleSheet(
            """
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;  /* Dark gray color */
                border-radius: 10px;
                border: 3px solid #7C2F3E;  /* Light gray border */
                padding: 10px 20px;
                font-size: 48px;
            }
            """
        )

        self.keypad_layout = QGridLayout(self.square_layout)
        self.create_number_buttons()

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.on_login_click)

        # Apply minimalist style to buttons
        self.apply_minimalist_style(self.login_button)

        # Add input field and login button to the keypad layout
        self.keypad_layout.addWidget(self.input_edit, 0, 0, 1, 3)
        self.keypad_layout.addWidget(self.login_button, 5, 1)

        # Layout setup
        main_layout = QVBoxLayout(central_widget)

        # Add square layout to main layout with alignment at the center
        main_layout.addWidget(self.square_layout, alignment=Qt.AlignCenter)

        # Back button
        self.back_bt = QPushButton("Back", self)
        self.back_bt.setFixedSize(150, 80)  # Set fixed size
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
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        self.back_bt.setFocusPolicy(Qt.NoFocus)
        self.back_bt.clicked.connect(self.go_back)
        self.back_bt.move(50, 65)  # Set position
        self.back_bt.show()

    def apply_minimalist_style(self, button):
        button.setStyleSheet(
            "QPushButton {"
            "background-color: #7C2F3E;"  # Blue color
            "color: #FFFFFF;"  # White text color
            "border-radius: 10px;"
            "padding: 20px 40px;"
            "font-size: 24px;"
            "}"
            "QPushButton:pressed {"
            "background-color: #D8973C;"  # Even darker blue color when pressed
            "}"
        )

    def create_number_buttons(self):
        numbers = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "Clear",
            "0",
            "Backspace",
        ]

        positions = [(i, j) for i in range(4) for j in range(3)]

        for position, number in zip(positions, numbers):
            row, col = position
            button = QPushButton(number)
            button.clicked.connect(self.on_button_click)
            self.keypad_layout.addWidget(button, row + 1, col)
            self.apply_minimalist_style(button)

    def on_button_click(self):
        clicked_button = self.sender()
        clicked_text = clicked_button.text()

        if clicked_text == "Clear":
            self.input_edit.clear()
        elif clicked_text == "Backspace":
            current_text = self.input_edit.text()
            self.input_edit.setText(current_text[:-1])
        else:
            current_text = self.input_edit.text()
            self.input_edit.setText(current_text + clicked_text)

    def on_login_click(self):
        input_text = self.input_edit.text()
        # Perform login validation here
        print("Login button clicked with input:", input_text)

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

    def go_back(self):
        self.setVisible(False)
        self.home_screen_backbt_clicked.emit()

    def on_login_click(self):
        input_password = self.input_edit.text()
        if input_password == self.admin_password:
            self.open_main_window()
        else:
            self.show_password_incorrect_message()

    def open_main_window(self):
        self.new_window = AdminScreenWindow()
        self.new_window.setVisible(True)
        self.setVisible(False)
        
        self.new_window.home_screen_backbt_clicked.connect(self.go_back)

    def show_password_incorrect_message(self):
        pass