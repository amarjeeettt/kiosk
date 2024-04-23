import cups
import sqlite3
import time
from datetime import datetime
from threading import Thread, Event
from gpiozero import Button
from PyQt5.QtWidgets import (
    QApplication,
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
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QSize


class PrintFormWindow(QMainWindow):
    print_preview_backbt_clicked = pyqtSignal()

    def __init__(self, label, value, total):
        super().__init__()
        self.set_background_image()
        self.showMaximized()

        form_label = label
        number_of_copy = value

        self.counter = 0
        self.bondpaper_quantity = None

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        top_button = QPushButton(self)
        top_button.setText("Cancel")
        top_button.clicked.connect(self.go_back)
        top_button.setStyleSheet(
            """
            QPushButton { 
                background-color: #A93F55; 
                color: #F3F7F0; 
                font-family: Montserrat;
                font-size: 24px; 
                padding-bottom: 10px;
                border-bottom-left-radius: 50px; 
                border-bottom-right-radius: 50px; 
            }
            """
        )
        top_button.setGeometry(778, 0, 125, 90)
        top_button.setFocusPolicy(Qt.NoFocus)  # Adjust the position here
        top_button.show()

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

        total_label = QLabel(f"₱{total:0.2f}")
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
        rectangle_layout.addWidget(rectangle)

        rectangle_inner_layout = QHBoxLayout()
        rectangle.setLayout(rectangle_inner_layout)

        text_label = QLabel("Please Pay\nExact Amount")
        text_label.setWordWrap(True)
        text_label.setStyleSheet(
            """
                QLabel { 
                    font-family: Roboto; 
                    padding-left: 105px; 
                    font-size: 24px; 
                }
            """
        )
        rectangle_inner_layout.addWidget(text_label)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)

        # Set stylesheet only for the vertical line
        line.setStyleSheet("QFrame { background-color: black; }")
        rectangle_inner_layout.addWidget(line)

        self.button = QPushButton("Print")
        self.button.setStyleSheet("QPushButton { font-size: 16px; }")
        rectangle_inner_layout.addWidget(self.button)

        self.button.clicked.connect(
            lambda: self.print_document(form_label, number_of_copy, total)
        )
        self.button.setEnabled(False)

        # self.counter_thread = CounterThread()
        # self.counter_thread.counter_changed.connect(
        #    lambda counter: self.update_counter(counter, total)
        # )
        # self.counter_thread.start()

    def update_counter(self, counter, total):
        self.counter = counter
        self.amount_label.setText(f"₱{self.counter:0.2f}")
        self.check_total_counter_match(total)

    def check_total_counter_match(self, total):
        if self.counter >= total:
            self.button.setEnabled(True)
        else:
            self.button.setEnabled(False)

    def print_document(self, form_label, number_of_copy, total):
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()
            printer_name = list(printers.keys())[0]
            file_path = f"./forms/{form_label}.pdf"

            for _ in range(number_of_copy):
                job_id = conn.printFile(printer_name, file_path, "Print Job", {})
                print("Print job submitted with ID:", job_id)

                if job_id is not None:
                    print_result = "Success"
                else:
                    print_result = "Failed"

                with sqlite3.connect("kiosk.db") as conn_sqlite:
                    cursor = conn_sqlite.cursor()

                    if print_result == "Success":
                        cursor.execute(
                            "UPDATE kiosk_settings SET bondpaper_quantity = bondpaper_quantity - 1"
                        )

                    cursor.execute(
                        "INSERT INTO kiosk_print_results (date_printed, form_name, quantity, total_price, result) VALUES (?, ?, ?, ?, ?)",
                        (
                            datetime.now(),
                            form_label,
                            number_of_copy,
                            total,
                            print_result,
                        ),
                    )

                    conn_sqlite.commit()
                    cursor.execute(
                        "SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1"
                    )
                    self.bondpaper_quantity = cursor.fetchone()[0]

                    print(self.bondpaper_quantity)

        except Exception as e:
            print("Error during printing:", e)

    def go_back(self):
        self.close()
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
        self.coinslot = Button(22)
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
