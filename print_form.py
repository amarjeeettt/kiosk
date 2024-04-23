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
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread


class PrintFormWindow(QMainWindow):
    print_preview_backbt_clicked = pyqtSignal()

    def __init__(self, label, value, total):
        super().__init__()

        self.setWindowTitle("PyQt Example")
        self.showMaximized()

        form_label = label
        number_of_copy = value

        self.counter = 0
        self.bondpaper_quantity = None

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.top_button = QPushButton("Top Button")
        self.top_button.clicked.connect(self.go_back)
        self.top_button.setStyleSheet("QPushButton { background-color: #A93F55; color: #F3F7F0; font-family: Montserrat;font-size: 20px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; }")
        self.top_button.setMinimumHeight(100)
        self.top_button.setMaximumWidth(100)
        self.top_button.setMinimumWidth(100)
        main_layout.addWidget(self.top_button, alignment=Qt.AlignHCenter)

        main_layout.addSpacerItem(
            QSpacerItem(40, 40, QSizePolicy.Minimum, QSizePolicy.Preferred)
        )

        squares_layout = QHBoxLayout()
        main_layout.addLayout(squares_layout)

        square1 = QWidget()
        square1.setStyleSheet("background-color: lightblue; border-radius: 45px;")
        square1_layout = QVBoxLayout()
        square1.setLayout(square1_layout)
        total_label = QLabel(f"Total: {total:0.2f}")
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("QLabel { font-size: 16px; }")
        square1_layout.addWidget(total_label)
        square1.setFixedSize(550, 550)
        squares_layout.addWidget(square1)

        squares_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        )

        self.square2_label = QLabel(str(self.counter))
        self.square2_label.setAlignment(Qt.AlignCenter)
        self.square2_label.setStyleSheet("QLabel { font-size: 16px; }")
        square2 = QWidget()
        square2.setStyleSheet("background-color: lightgreen; border-radius: 45px;")
        square2_layout = QVBoxLayout()
        square2.setLayout(square2_layout)
        square2_layout.addWidget(self.square2_label)
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
        rectangle_layout.addWidget(rectangle)

        rectangle_inner_layout = QHBoxLayout()
        rectangle.setLayout(rectangle_inner_layout)

        text_label = QLabel("Text Label")
        text_label.setStyleSheet("QLabel { font-size: 16px; }")
        rectangle_inner_layout.addWidget(text_label)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        rectangle_inner_layout.addWidget(line)

        self.button = QPushButton("Button")
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
        self.square2_label.setText(str(self.counter))
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
