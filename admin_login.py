import sqlite3
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, pyqtSignal
from custom_message_box import CustomMessageBox


class AdminLoginWidget(QWidget):
    # Signals for back button and login button clicks
    home_screen_backbt_clicked = pyqtSignal()
    login_clicked = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Set up the main layout
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
        layout.addLayout(back_button_layout)

        # Connect to the database to retrieve the admin password
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()
        cursor.execute("SELECT admin_password FROM kiosk_settings LIMIT 1")
        self.admin_password = cursor.fetchone()[0]
        conn.close()

        # Create a white background square layout for the keypad and input field
        self.square_layout = QWidget()
        self.square_layout.setStyleSheet(
            """     
            background-color: #FFFFFF; 
            border: 1px solid #CCCCCC;
            border-radius: 30px;
            """
        )
        self.square_layout.setContentsMargins(50, 0, 50, 0)
        self.square_layout.setFixedSize(800, 800)

        # Add a drop shadow effect to the square layout
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(50)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 12)
        self.square_layout.setGraphicsEffect(shadow_effect)

        # Create the input field for the password
        self.input_edit = QLineEdit()
        self.input_edit.setAlignment(Qt.AlignCenter)
        self.input_edit.setEchoMode(QLineEdit.Password)
        self.input_edit.setMaxLength(4)
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

        # Create the keypad layout
        self.keypad_layout = QGridLayout(self.square_layout)
        self.create_number_buttons()

        # Create the login button
        self.login_button = QPushButton("Login")
        self.login_button.setFocusPolicy(Qt.NoFocus)
        self.login_button.clicked.connect(self.on_login_click)
        self.apply_minimalist_style(self.login_button)

        # Add the input field and login button to the keypad layout
        self.keypad_layout.addWidget(self.input_edit, 0, 0, 1, 3)
        self.keypad_layout.addWidget(self.login_button, 5, 1)

        layout.addWidget(self.square_layout, alignment=Qt.AlignCenter)

    def apply_minimalist_style(self, button):
        # Apply a minimalist style to buttons
        button.setStyleSheet(
            "QPushButton {"
            "background-color: #7C2F3E;"  # Button color
            "color: #FFFFFF;"  # Text color
            "border-radius: 10px;"
            "padding: 20px 40px;"
            "font-size: 24px;"
            "}"
            "QPushButton:pressed {"
            "background-color: #D8973C;"  # Button color when pressed
            "}"
        )

    def create_number_buttons(self):
        # Create number buttons and add them to the keypad layout
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
            button.setFocusPolicy(Qt.NoFocus)
            button.clicked.connect(self.on_button_click)
            self.keypad_layout.addWidget(button, row + 1, col)
            self.apply_minimalist_style(button)

    def on_button_click(self):
        # Handle button clicks on the keypad
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

    def go_back(self):
        # Emit signal and clear the input field when back button is clicked
        self.setVisible(False)
        self.input_edit.clear()
        self.home_screen_backbt_clicked.emit()

    def on_login_click(self):
        # Handle login button click and validate the password
        input_password = self.input_edit.text()

        if input_password == self.admin_password:
            self.setVisible(False)
            self.input_edit.clear()
            self.login_clicked.emit()
        else:
            # Show an error message if the password is incorrect
            message_box = CustomMessageBox(
                "Error",
                "Incorrect password. Please try again.",
                parent=self,
            )
            message_box.exec_()
            self.input_edit.clear()
