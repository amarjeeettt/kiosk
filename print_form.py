import sqlite3
import time
from threading import Event
from gpiozero import Button
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMainWindow,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QDesktopWidget,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from print_window import PrintWindow


class PrintFormWindow(QMainWindow):
    print_preview_backbt_clicked = pyqtSignal()

    def __init__(self, label, value, total, num_of_pages):
        super().__init__()
        self.set_background_image()
        self.showMaximized()

        # Connect database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        self.coins_left = cursor.fetchone()[0]

        conn.close()

        self.form_label = label
        self.total = total
        self.number_of_copy = value
        self.number_of_page = num_of_pages

        self.counter = self.coins_left
        self.bondpaper_quantity = None

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        cancel_bt = QPushButton(self)
        cancel_bt.setText("Cancel")
        cancel_bt.clicked.connect(self.go_back)
        cancel_bt.setStyleSheet(
            """
            QPushButton { 
                background-color: #7C2F3E; 
                color: #FAEBD7; 
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold; 
                padding-bottom: 10px;
                border-bottom-left-radius: 50px; 
                border-bottom-right-radius: 50px; 
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        cancel_bt.setGeometry(893, 0, 125, 90)
        cancel_bt.setFocusPolicy(Qt.NoFocus)  # Adjust the position here
        cancel_bt.show()

        main_layout.addSpacerItem(
            QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)
        )

        squares_layout = QHBoxLayout()
        main_layout.addLayout(squares_layout)

        square1 = QWidget()
        square1.setStyleSheet("background-color: #FDFDFD; border-radius: 85px;")
        square1_layout = QVBoxLayout()
        square1.setLayout(square1_layout)

        top_total_label = QLabel("Total")
        top_total_label.setStyleSheet(
            """
            QLabel { 
                font-family: Roboto;
                font-size: 22px; 
                margin-top: 185px;
            }
            """
        )
        top_total_label.setAlignment(Qt.AlignCenter)

        total_label = QLabel(f"₱{self.total:0.2f}")
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet(
            """
            QLabel { 
                font-family: Monterrat;
                font-weight: bold;
                font-size: 82px; 
                letter-spacing: 5px;
                color: #7B0323;
                margin-bottom: 200px;
            }
            """
        )

        # Create a shadow effect for square1
        shadow_effect1 = QGraphicsDropShadowEffect()
        shadow_effect1.setBlurRadius(50)
        shadow_effect1.setColor(Qt.gray)
        shadow_effect1.setOffset(0, 15)

        square1.setFixedSize(550, 550)
        square1.setGraphicsEffect(shadow_effect1)

        square1.setFixedSize(550, 550)
        squares_layout.addWidget(square1)

        # Adjust the spacing and alignment
        square1_layout.addWidget(top_total_label, alignment=Qt.AlignCenter)
        square1_layout.addWidget(total_label, alignment=Qt.AlignCenter)
        square1_layout.setSpacing(0)

        squares_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        )

        top_amount_label = QLabel("Amount Paid")
        top_amount_label.setAlignment(Qt.AlignCenter)
        top_amount_label.setStyleSheet(
            """
            QLabel { 
                font-family: Roboto;
                font-size: 22px; 
                margin-top: 185px;
            }
            """
        )

        self.amount_label = QLabel(f"₱{self.counter:0.2f}")
        self.amount_label.setAlignment(Qt.AlignCenter)
        self.amount_label.setStyleSheet(
            """
            QLabel { 
                font-family: Monterrat;
                font-weight: bold;
                font-size: 82px; 
                letter-spacing: 5px;
                color: #7B0323;
                margin-bottom: 200px;
            }
            """
        )

        square2 = QWidget()
        square2.setStyleSheet("background-color: #FDFDFD; border-radius: 85px;")

        square2_layout = QVBoxLayout()
        square2.setLayout(square2_layout)

        square2_layout.addWidget(top_amount_label, alignment=Qt.AlignCenter)
        square2_layout.addWidget(self.amount_label, alignment=Qt.AlignCenter)
        square2.setFixedSize(550, 550)

        # Create a shadow effect for square2
        shadow_effect2 = QGraphicsDropShadowEffect()
        shadow_effect2.setBlurRadius(50)
        shadow_effect2.setColor(Qt.gray)
        shadow_effect2.setOffset(0, 15)

        square2.setGraphicsEffect(shadow_effect2)

        squares_layout.addWidget(square2)

        main_layout.addSpacerItem(
            QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)
        )

        rectangle_layout = QHBoxLayout()
        main_layout.addLayout(rectangle_layout)

        rectangle = QFrame()
        rectangle.setFrameShape(QFrame.StyledPanel)
        rectangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        rectangle.setFixedSize(850, 150)
        rectangle.setStyleSheet(
            "QFrame { background-color: #FDFDFD; border-radius: 30px; }"
        )

        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(30)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 12)  # Adjust the shadow's offset as needed

        # Apply the effect to the rectangle
        rectangle.setGraphicsEffect(shadow_effect)

        rectangle_layout.addWidget(rectangle)

        rectangle_inner_layout = QHBoxLayout()
        rectangle.setLayout(rectangle_inner_layout)

        text_label = QLabel("Please Pay\nExact Amount")
        text_label.setWordWrap(True)
        text_label.setStyleSheet(
            """
                QLabel { 
                    font-family: Roboto; 
                    padding-left: 115px; 
                    font-size: 20px; 
                }
            """
        )
        rectangle_inner_layout.addWidget(text_label, alignment=Qt.AlignVCenter)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFixedHeight(90)
        # Set stylesheet only for the vertical line
        line.setStyleSheet("QFrame { background-color: black; }")
        rectangle_inner_layout.addWidget(line, alignment=Qt.AlignCenter)

        self.print_bt = QPushButton("Print")
        self.print_bt.setFixedSize(250, 80)
        self.print_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E; 
                color: #FAEBD7; 
                font-family: Montserrat;
                border: none;
                text-align: center;
                font-weight: bold;
                font-size: 18px;
                margin: 4px 2px;
                border-radius: 12px;
                padding: 20px 40px;
                }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            QPushButton:disabled {
                background-color: #C0C0C0; /* Light Grey */
                color: #808080; /* Dark Grey */
            }
            """
        )
        rectangle_inner_layout.addWidget(self.print_bt)

        self.print_bt.clicked.connect(self.open_print_window)
        self.print_bt.setEnabled(False)

        # Add spacer item to push the line to the center
        rectangle_inner_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        )

        self.check_total_counter_match()

        # self.counter_thread = CounterThread()
        # self.counter_thread.counter_changed.connect(
        #    lambda counter: self.update_counter(counter)
        # )
        # self.counter_thread.start()

    def update_counter(self, counter):
        self.counter = counter
        self.amount_label.setText(f"₱{self.counter:0.2f}")

        # Connect database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE kiosk_settings SET coins_left = ?",
            (self.counter,),
        )
        conn.commit()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        coins = cursor.fetchone()[0]
        conn.close()

        print(coins)
        self.check_total_counter_match()

    def check_total_counter_match(self):
        if self.counter >= self.total:
            self.print_bt.setEnabled(True)
        else:
            self.print_bt.setEnabled(False)

    def open_print_window(self):
        # Stop the thread and close coinslot connection
        # self.counter_thread.stop()
        coins = self.counter - self.total

        self.print_window = PrintWindow(
            self.form_label, self.number_of_page, self.number_of_copy, self.total, coins
        )
        self.print_window.setVisible(True)
        self.setVisible(False)

    def go_back(self):
        # Stop the thread and close coinslot connection
        # self.counter_thread.stop()
        self.setVisible(False)
        self.print_preview_backbt_clicked.emit()

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


class CounterThread(QThread):
    counter_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.coinslot = Button(11)
        self.stop_event = Event()

    def run(self):
        counter = 0
        while not self.stop_event.is_set():
            try:
                if self.coinslot.is_pressed:
                    counter += 1
                    time.sleep(0.05)
                    self.counter_changed.emit(counter)
            except Exception as e:
                print(f"Error reading button state: {e}")

    def stop(self):
        self.stop_event.set()
        # Close the coinslot connection
        self.coinslot.close()
