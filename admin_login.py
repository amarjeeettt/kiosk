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
from PyQt5.QtCore import Qt, QTimer, QEvent, pyqtSignal


class AdminLoginWidget(QWidget):
    home_screen_backbt_clicked = pyqtSignal()
    login_clicked = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(30000)
        self.inactivity_timer.timeout.connect(self.go_back)
        self.inactivity_timer.start()

        self.installEventFilter(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        # layout.setAlignment(Qt.AlignCenter)

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

        # Connect database
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT admin_password FROM kiosk_settings LIMIT 1")
        self.admin_password = cursor.fetchone()[0]

        conn.close()

        # Create a white background square layout
        self.square_layout = QWidget()
        self.square_layout.setStyleSheet(
            """     
            background-color: #FFFFFF; 
            border: 1px solid #CCCCCC;
            border-radius: 30px;
            """
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
        self.login_button.setFocusPolicy(Qt.NoFocus)
        self.login_button.clicked.connect(self.on_login_click)

        # Apply minimalist style to buttons
        self.apply_minimalist_style(self.login_button)

        # Add input field and login button to the keypad layout
        self.keypad_layout.addWidget(self.input_edit, 0, 0, 1, 3)
        self.keypad_layout.addWidget(self.login_button, 5, 1)

        layout.addWidget(self.square_layout, alignment=Qt.AlignCenter)

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
            button.setFocusPolicy(Qt.NoFocus)
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

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.MouseButtonPress, QEvent.KeyPress]:
            self.reset_inactivity_timer()
        return super().eventFilter(obj, event)

    def reset_inactivity_timer(self):
        self.inactivity_timer.start()

    def go_back(self):
        self.setVisible(False)
        self.input_edit.clear()

        print("No user interaction for 30 seconds.")
        self.inactivity_timer.stop()

        self.home_screen_backbt_clicked.emit()

    def on_login_click(self):
        input_password = self.input_edit.text()

        if input_password == self.admin_password:
            self.setVisible(False)
            self.input_edit.clear()

            self.inactivity_timer.stop()

            self.login_clicked.emit()
