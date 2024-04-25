import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QGridLayout
from PyQt5.QtCore import Qt

class SquareLayout(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a white background square layout
        self.square_layout = QWidget()
        self.square_layout.setStyleSheet("background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 20px;")  # Updated styling
        self.square_layout.setContentsMargins(50, 0, 50, 0)
        self.square_layout.setFixedSize(800, 800)

        # Create widgets
        self.input_edit = QLineEdit()
        self.input_edit.setAlignment(Qt.AlignCenter)
        self.input_edit.setEchoMode(QLineEdit.Password)
        self.input_edit.setStyleSheet(
            "QLineEdit {"
            "background-color: #F0F0F0;"
            "color: #333333;"  # Dark gray color
            "border-radius: 10px;"
            "border: 1px solid #CCCCCC;"  # Light gray border
            "padding: 10px 20px;"
            "font-size: 48px;"
            "}"
            "QLineEdit:hover {"
            "background-color: #E5E5E5;"
            "}"
            "QLineEdit:focus {"
            "background-color: #FFFFFF;"
            "border-color: #007AFF;"  # Blue border on focus
            "}"
        )

        self.keypad_layout = QGridLayout(self.square_layout)
        self.create_number_buttons()
        
        # Login button
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.on_login_click)
        
        # Apply minimalist style to buttons
        self.apply_minimalist_style(self.login_button)
        
        # Add input field and login button to the keypad layout
        self.keypad_layout.addWidget(self.input_edit, 0, 0, 1, 3)
        self.keypad_layout.addWidget(self.login_button, 5, 1)
        
        # Layout setup
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.square_layout, alignment=Qt.AlignCenter)

    def apply_minimalist_style(self, button):
        button.setStyleSheet(
            "QPushButton {"
            "background-color: #007AFF;"  # Blue color
            "color: #FFFFFF;"  # White text color
            "border-radius: 10px;"
            "border: 1px solid #007AFF;"  # Blue border
            "padding: 20px 40px;"
            "font-size: 24px;"
            "}"
            "QPushButton:hover {"
            "background-color: #0056b3;"  # Darker blue color on hover
            "}"
            "QPushButton:pressed {"
            "background-color: #004080;"  # Even darker blue color when pressed
            "}"
        )

    def create_number_buttons(self):
        numbers = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            'Clear', '0', 'Backspace'
        ]
        
        positions = [(i, j) for i in range(4) for j in range(3)]
        
        for position, number in zip(positions, numbers):
            row, col = position
            button = QPushButton(number)
            button.clicked.connect(self.on_button_click)
            self.keypad_layout.addWidget(button, row+1, col)
            self.apply_minimalist_style(button)

    def on_button_click(self):
        clicked_button = self.sender()
        clicked_text = clicked_button.text()

        if clicked_text == 'Clear':
            self.input_edit.clear()
        elif clicked_text == 'Backspace':
            current_text = self.input_edit.text()
            self.input_edit.setText(current_text[:-1])
        else:
            current_text = self.input_edit.text()
            self.input_edit.setText(current_text + clicked_text)

    def on_login_click(self):
        input_text = self.input_edit.text()
        # Perform login validation here
        print("Login button clicked with input:", input_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    num_pad = SquareLayout()
    num_pad.setWindowTitle('Number Pad')
    num_pad.showMaximized()
    sys.exit(app.exec_())
