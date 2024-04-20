import cups
import sqlite3
import time
from threading import Thread
from gpiozero import Button
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread

class PrintFormWindow(QMainWindow):
    print_preview_backbt_clicked = pyqtSignal()

    def __init__(self, label, value, total):
        super().__init__()

        self.setWindowTitle("PyQt Example")
        self.showMaximized()
        
        form_label = label
        number_of_copy = value
        
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
        self.square2_label = QLabel(str(self.counter))
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
        
        # Connect button clicked signal to print function
        self.button.clicked.connect(lambda: self.print_document(form_label, number_of_copy))
        
        # Disable the button initially
        self.button.setEnabled(False)
        
        self.counter_thread = CounterThread()
        self.counter_thread.counter_changed.connect(lambda counter: self.update_counter(counter, total))
        self.counter_thread.start()


    def update_counter(self, counter, total):  
        self.counter = counter
        self.square2_label.setText(str(self.counter))
        # Check if total and counter match
        self.check_total_counter_match(total)


    def check_total_counter_match(self, total):
        # Check if total and counter match
        if self.counter >= total:
            self.button.setEnabled(True)
        else:
            self.button.setEnabled(False)


    # Modify the print_document method
    def print_document(self, form_label, number_of_copy):
        # Connect to the local CUPS server
        conn = cups.Connection()

        # Get a list of available printers
        printers = conn.getPrinters()

        # Get the first printer in the list
        printer_name = list(printers.keys())[0]

        # Specify the file you want to print
        file_path = f"{form_label}.pdf"

        # Print the file
        for _ in range(number_of_copy):
            job_id = conn.printFile(printer_name, file_path, "Print Job", {})
            print("Print job submitted with ID:", job_id)

            # After successful print, decrement bondpaper_quantity in kiosk_setting table
            try:
                # Connect to the SQLite database
                with sqlite3.connect('kiosk.db') as conn_sqlite:
                    cursor = conn_sqlite.cursor()

                    # Execute the SQL UPDATE query
                    cursor.execute("UPDATE kiosk_settings SET bondpaper_quantity = bondpaper_quantity - 1")
                    conn_sqlite.commit()  # Commit the transaction
                    
                    cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
                    self.bondpaper_quantity = cursor.fetchone()[0]
            
                    print(self.bondpaper_quantity)
                    
            except sqlite3.Error as e:
                print("SQLite error:", e)
        

    def go_back(self):
        self.close()
        self.print_preview_backbt_clicked.emit()


class CounterThread(QThread):
    counter_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.coinslot = None
        self.coinslotState = True

    def run(self):
        self.coinslot = Button(22)  # Initialize the Button object here
        counter = 0
        while True:
            while self.coinslotState:
                try:
                    if self.coinslot.is_pressed:
                        counter += 1
                        time.sleep(0.05)
                        self.counter_changed.emit(counter)
                except Exception as e:
                    print(f"Error reading button state: {e}")