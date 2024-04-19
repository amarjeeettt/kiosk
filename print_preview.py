import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from view_process import ViewProcessWindow
from print_form import PrintFormWindow

class PrintPreviewWindow(QMainWindow):
    view_form_backbt_clicked = pyqtSignal()
    
    def __init__(self, label, index):
        super().__init__()

        self.setWindowTitle("Print Preview")
        self.showMaximized()
        
        # connect database
        conn = sqlite3.connect('kiosk.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT base_price FROM kiosk_settings LIMIT 1")
        self.base_price = cursor.fetchone()[0]
        
        cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
        self.bondpaper_quantity = cursor.fetchone()[0]
        
        conn.close()

        # Left window
        left_window = QWidget()
        left_window.setFixedWidth(200)  # Set fixed width
        left_layout = QVBoxLayout(left_window)  # Use QVBoxLayout
        left_layout.setAlignment(Qt.AlignTop)  # Align top
        back_bt = QPushButton("Back Button")
        back_bt.setFixedSize(200, 100)  # Set fixed size
        back_bt.clicked.connect(self.go_back)
        # Apply margin to the left button
        back_bt.setStyleSheet("margin-top: 20px;")
        left_layout.addWidget(back_bt)

        # Center image
        img_index = index
        center_image = QLabel()
        pixmap = QPixmap(f"img/{img_index}.png")  # Replace "image.jpg" with your image file
        center_image.setPixmap(pixmap.scaled(850, 850, Qt.KeepAspectRatio))
        center_image.setAlignment(Qt.AlignCenter)

        # Right label
        form_label = label
        right_label = QLabel(form_label)
        right_label.setStyleSheet("margin-top: 80px; margin-bottom: 60px")
        right_layout = QVBoxLayout()
        right_layout.addWidget(right_label, alignment=Qt.AlignCenter)  # Align label in center
        
        # Bottom square inside right_label layout
        square_frame = QFrame()
        square_frame.setStyleSheet("background-color: #FFFFFF; border-radius: 45px;")
        # Set the size of the square frame
        square_frame.setFixedSize(420, 360)
        square_frame.setFrameStyle(QFrame.Box)
        square_frame_layout = QVBoxLayout(square_frame)
        square_label = QLabel("Square Label")
        square_frame_layout.addWidget(square_label, alignment=Qt.AlignCenter)  # Align label in center
        
        self.total = self.base_price
        self.total_label = QLabel(f"Total: {self.total:0.2f}")  # Initialize total label with base price
        square_frame_layout.addWidget(self.total_label, alignment=Qt.AlignCenter)  # Align label in center
        square_layout = QHBoxLayout()  # Layout for buttons and label
        square_button1 = QPushButton("-")
        square_button1.setStyleSheet(
            """
            QPushButton {
                background-color: #7B0323;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
                color: white;
            }
            """
        )
        square_button2 = QPushButton("+")
        square_button2.setStyleSheet(
            """
            QPushButton {
                background-color: #7B0323;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #007BAA;
                color: white;
            }
            """
        )
        self.value = 1
        self.label_between_buttons = QLabel(str(self.value))
        square_button1.clicked.connect(self.decrement_value)
        square_button2.clicked.connect(self.increment_value)
        
        # Set margin for the square layout
        square_layout.setContentsMargins(80, 80, 80, 30) # right, top, left, bottom
        
        square_layout.addWidget(square_button1)
        square_layout.addWidget(self.label_between_buttons, alignment=Qt.AlignCenter)  # Align label at center
        square_layout.addWidget(square_button2)
        square_frame_layout.addLayout(square_layout)
        right_layout.addWidget(square_frame)

        # Outer buttons
        view_process_bt = QPushButton("View Process")
        view_process_bt.setFixedSize(250, 150)  # Set fixed size
        view_process_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
                color: white;
            }
            """
        )
        view_process_bt.clicked.connect(lambda: self.view_process_window(form_label))
        
        
        print_bt = QPushButton("Print")
        print_bt.setFixedSize(250, 150)  # Set fixed size
        print_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #008CBA;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #007BAA;
                color: white;
            }
            """
        )
        print_bt.clicked.connect(lambda: self.print_form_window(form_label))
        # Add vertical spacer item between square frame and outer buttons
        spacer_vertical = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        right_layout.addItem(spacer_vertical)
        
        right_layout.addWidget(view_process_bt, alignment=Qt.AlignCenter)
        right_layout.addWidget(print_bt, alignment=Qt.AlignCenter)

        # Add spacer item between center image and right layout
        spacer_left = QSpacerItem(120, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        spacer_right = QSpacerItem(140, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        spacer = QSpacerItem(100, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_window)
        main_layout.addItem(spacer_left)
        main_layout.addWidget(center_image)
        main_layout.addItem(spacer_right)
        
        # Add right_layout as a widget with alignment
        widget = QWidget()
        widget.setLayout(right_layout)
        main_layout.addWidget(widget, alignment=Qt.AlignTop | Qt.AlignCenter)  # Align right layout to top
        
        main_layout.addItem(spacer)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
    def increment_value(self):
        if self.value < self.bondpaper_quantity:
            self.value += 1
            self.label_between_buttons.setText(str(self.value))
            self.update_total_label()
        
    def decrement_value(self):
        if self.value > 0:
            self.value -= 1
            self.label_between_buttons.setText(str(self.value))
            self.update_total_label()
            
    def update_total_label(self):
        self.total = self.base_price * self.value
        self.total_label.setText(f"Total: {self.total:0.2f}")
    
    def view_process_window(self, form_label):
        self.close()
        self.new_window = ViewProcessWindow(form_label)
        self.new_window.show()
    
    def print_form_window(self, form_label):
        self.close()
        self.new_window = PrintFormWindow(form_label, self.value, self.total)
        self.new_window.show()
        self.new_window.print_preview_backbt_clicked.connect(self.go_back_to_print_preview)
    
    def go_back(self):
        self.close()
        self.view_form_backbt_clicked.emit()
    
    def go_back_to_print_preview(self):
        self.close()
        self.show()
