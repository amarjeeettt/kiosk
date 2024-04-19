import sys
import time
from gpiozero import Button
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

class PrintFormWindow(QMainWindow):
    print_preview_backbt_clicked = pyqtSignal()

    def __init__(self, label, value, total):
        super().__init__()

        self.setWindowTitle("PyQt Example")
        self.showMaximized()

        # Initialize counter
        self.counter = 0

        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create main layout
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Create button at the top center
        self.top_button = QPushButton("Top Button")
        self.top_button.clicked.connect(self.go_back)
        self.top_button.setStyleSheet("QPushButton { font-size: 20px; }")
        self.top_button.setMaximumWidth(200)
        self.top_button.setMinimumWidth(200)
        main_layout.addWidget(self.top_button, alignment=Qt.AlignHCenter)

        # Add spacer between top button and squares
        main_layout.addSpacerItem(QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Preferred))

        # Create squares layout
        squares_layout = QHBoxLayout()
        main_layout.addLayout(squares_layout)

        # Create first square
        square1 = QWidget()
        square1.setStyleSheet("background-color: lightblue; border-radius: 45px;")
        square1_layout = QVBoxLayout()
        square1.setLayout(square1_layout)
        total_label = QLabel(f"Total: {total:0.2f}")
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("QLabel { font-size: 16px; }")
        square1_layout.addWidget(total_label)
        # Set size for square1
        square1.setFixedSize(550, 550)
        squares_layout.addWidget(square1)

        # Add spacer between squares
        squares_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Preferred, QSizePolicy.Minimum))

        # Create second square
        self.square2_label = QLabel("0")
        self.square2_label.setAlignment(Qt.AlignCenter)
        self.square2_label.setStyleSheet("QLabel { font-size: 16px; }")
        square2 = QWidget()
        square2.setStyleSheet("background-color: lightgreen; border-radius: 45px;")
        square2_layout = QVBoxLayout()
        square2.setLayout(square2_layout)
        square2_layout.addWidget(self.square2_label)
        # Set size for square2
        square2.setFixedSize(550, 550)
        squares_layout.addWidget(square2)

        # Add spacer between squares and rectangle
        main_layout.addSpacerItem(QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Preferred))

        # Create rectangle layout
        rectangle_layout = QHBoxLayout()
        main_layout.addLayout(rectangle_layout)

        # Create rectangle
        rectangle = QFrame()
        rectangle.setFrameShape(QFrame.StyledPanel)

        # Set size policy for the rectangle
        rectangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        rectangle.setFixedSize(850, 150)  # Set size to 850 x 150

        rectangle_layout.addWidget(rectangle)

        # Create layout for rectangle
        rectangle_inner_layout = QHBoxLayout()
        rectangle.setLayout(rectangle_inner_layout)

        # Create text label and button inside rectangle
        text_label = QLabel("Text Label")
        text_label.setStyleSheet("QLabel { font-size: 16px; }")
        rectangle_inner_layout.addWidget(text_label)

        # Create separator line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        rectangle_inner_layout.addWidget(line)

        self.button = QPushButton("Button")
        self.button.setStyleSheet("QPushButton { font-size: 16px; }")
        rectangle_inner_layout.addWidget(self.button)

        # Disable the button initially
        self.button.setEnabled(False)

        # Create coin slot and start monitoring
        self.coinslot = Button(22)
        self.coinslot.when_pressed = self.coin_detected

        # Start a timer to periodically check if total and counter match
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.check_total_counter_match(total))
        self.timer.start(1000)  # Check every second

    def coin_detected(self):
        self.counter += 1
        self.square2_label.setText(str(self.counter))

    def check_total_counter_match(self, total):
        # Check if total and counter match
        if self.counter >= total:
            self.button.setEnabled(True)
        else:
            self.button.setEnabled(False)

    def go_back(self):
        self.close()
        self.print_preview_backbt_clicked.emit()