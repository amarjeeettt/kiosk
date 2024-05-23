import time
import sqlite3
from gpiozero import Button
from threading import Event
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from print_window import PrintMessageBox


class PrintFormWidget(QWidget):
    go_back_home = pyqtSignal()
    cancel_clicked = pyqtSignal()

    def __init__(self, parent, title, num_copy, num_pages, total):
        super().__init__(parent)
        self.setup_ui(title, num_copy, num_pages, total)

    def setup_ui(self, title, num_copy, num_pages, total):
        self.title = title
        self.num_copy = num_copy
        self.num_pages = num_pages
        self.total = total

        # Connect to the database and retrieve the initial counter value
        self.connect_db()

        # Create a layout for the central widget
        layout = QVBoxLayout(self)

        # Create the button
        self.cancel_bt = QPushButton("Cancel")
        self.cancel_bt.setFocusPolicy(Qt.NoFocus)
        self.cancel_bt.setFixedSize(125, 90)
        self.cancel_bt.setStyleSheet(
            """
            QPushButton { 
                background-color: #7C2F3E; 
                color: #FAEBD7; 
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold; 
                border-radius: 45px; 
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        self.cancel_bt.clicked.connect(self.go_back)

        layout.addWidget(self.cancel_bt, alignment=Qt.AlignCenter)

        squares_layout = QHBoxLayout()

        squares_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Preferred, QSizePolicy.Minimum)
        )

        square1 = QWidget()
        square1.setStyleSheet(
            """
            background-color: #FDFDFD;
            border-radius: 85px;
            """
        )
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
        squares_layout.setContentsMargins(0, 0, 0, 0)

        rectangle_layout = QHBoxLayout()

        rectangle = QFrame()
        rectangle.setFrameShape(QFrame.StyledPanel)
        rectangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        rectangle.setFixedSize(850, 150)
        rectangle.setStyleSheet(
            """
            QFrame {
                background-color: #FDFDFD;
                border-radius: 30px;
            }
            """
        )

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(30)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 12)

        rectangle.setGraphicsEffect(shadow_effect)

        rectangle_layout.addWidget(rectangle)

        rectangle_inner_layout = QHBoxLayout()
        rectangle.setLayout(rectangle_inner_layout)

        text_label = QLabel("Please Pay\nExact Amount")
        text_label.setWordWrap(True)
        text_label.setStyleSheet(
            """
            QLabel {
                font-family: Open Sans;
                padding-left: 115px;
                font-size: 20px;
            }
            """
        )
        rectangle_inner_layout.addWidget(text_label, alignment=Qt.AlignVCenter)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFixedHeight(90)
        line.setStyleSheet(
            """
            QFrame {
                background-color: black;
            }
            """
        )
        rectangle_inner_layout.addWidget(line, alignment=Qt.AlignCenter)

        self.print_bt = QPushButton("Print")
        self.print_bt.setFocusPolicy(Qt.NoFocus)
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
        rectangle_layout.setContentsMargins(0, 0, 0, 80)

        layout.addLayout(squares_layout)
        layout.addSpacerItem(
            QSpacerItem(40, 60, QSizePolicy.Preferred, QSizePolicy.Minimum)
        )
        layout.addLayout(rectangle_layout)

        self.counter_thread = CounterThread(self.counter)
        self.counter_thread.counter_changed.connect(self.update_counter)
        self.counter_thread.start()

        self.check_total_counter_match()

    def connect_db(self):
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        self.coins_left = cursor.fetchone()[0]

        conn.close()

        self.counter = self.coins_left
        # self.counter = 10

    def update_counter(self, counter):
        self.counter = counter
        self.amount_label.setText(f"₱{self.counter:0.2f}")

        self.update_db_counter(self.counter)
        self.check_total_counter_match()

    def update_db_counter(self, counter):
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE kiosk_settings SET coins_left = ?",
            (counter,),
        )
        conn.commit()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        coins = cursor.fetchone()[0]
        conn.close()

        print(coins)

    def check_total_counter_match(self):
        if self.counter >= self.total:
            self.print_bt.setEnabled(True)
        else:
            self.print_bt.setEnabled(False)

    def open_print_window(self):
        self.counter_thread.stop()
        if self.counter > self.total:
            message_box = PrintMessageBox(
                self.title,
                self.num_copy,
                self.num_pages,
                self.total,
                False,
                parent=self,
            )
            parent_pos = self.mapToGlobal(self.rect().center())
            message_box.move(parent_pos - message_box.rect().center())
            message_box.go_back_to_home.connect(self.go_back_home_screen)
            message_box.exec_()

        elif self.counter == self.total:
            message_box = PrintMessageBox(
                self.title,
                self.num_copy,
                self.num_pages,
                self.total,
                True,
                parent=self,
            )
            parent_pos = self.mapToGlobal(self.rect().center())
            message_box.move(parent_pos - message_box.rect().center())
            message_box.go_back_to_home.connect(self.go_back_home_screen)
            message_box.exec_()

    def go_back(self):
        self.counter_thread.stop()
        self.setVisible(False)
        self.cancel_clicked.emit()

    def go_back_home_screen(self):
        self.counter_thread.stop()
        self.close()
        self.go_back_home.emit()


class CounterThread(QThread):
    counter_changed = pyqtSignal(int)

    def __init__(self, initial_counter):
        super().__init__()
        self.coinslot = Button(16)
        self.stop_event = Event()
        self.counter = initial_counter

    def run(self):
        while not self.stop_event.is_set():
            try:
                if self.coinslot.is_pressed:
                    self.counter += 1
                    time.sleep(0.05)
                    self.counter_changed.emit(self.counter)
            except Exception as e:
                print(f"Error reading button state: {e}")

    def stop(self):
        self.stop_event.set()
        self.coinslot.close()
