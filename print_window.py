import cups
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QProgressBar, QDesktopWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QMovie

class PrintWindow(QMainWindow):
    def __init__(self, form_label, number_of_page, number_of_copy, total):
        super().__init__()
        self.set_background_image()
        self.showMaximized()  # Show window maximized

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # Align layout in the center of the window
        central_widget.setLayout(layout)

        # Add image label
        image_label = QLabel()
        movie = QMovie("./img/animated_printer.gif")
        image_label.setMovie(movie)
        movie.start()
        layout.addWidget(image_label, alignment=Qt.AlignCenter)

        # Add LoadingWidget
        loading_widget = LoadingWidget()
        layout.addWidget(loading_widget)
        
        # Add label with dynamic period
        self.label = QLabel("Printing in Progress: Please wait for a moment.")
        self.label.setStyleSheet("font-family: Roboto; font-size: 14px; color: #19323C")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # Start timer to update label text
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateLabel)
        self.timer.start(500)  # Update every 500 milliseconds
        
        self.print_document(form_label, number_of_page, number_of_copy, total)
        
        
    def updateLabel(self):
        text = self.label.text()
        if text.endswith('....'):
            text = text[:-4]  # Remove the last four characters
        else:
            text += '.'  # Add a period
        self.label.setText(text)


    def print_document(self, form_label, number_of_page, number_of_copy, total):
        bondpaper_left = number_of_copy * number_of_page
        print_result = None

        try:
            conn = cups.Connection()
            printers = conn.getPrinters()
            printer_name = list(printers.keys())[0]
            file_path = f"./forms/{form_label}.pdf"

            # Define printer options (margin, orientation, custom paper size)
            printer_options = {
                'media': 'legal',  # Set custom paper size to 8.5 x 13 inches
            }

            for _ in range(number_of_copy):
                try:
                    job_id = conn.printFile(printer_name, file_path, "Print Job", printer_options)
                    print("Print job submitted with ID:", job_id)
                    if job_id is not None:
                        print_result = "Success"
                except Exception as e:
                    print("Print job failed:", e)
                    print_result = "Failed"

        except Exception as e:
            print("Error during printing:", e)
            print_result = "Failed"

        finally:
            conn = None

            with sqlite3.connect("kiosk.db") as conn_sqlite:
                cursor = conn_sqlite.cursor()

                if print_result == "Success":
                    cursor.execute(
                        "UPDATE kiosk_settings SET bondpaper_quantity = bondpaper_quantity - ?",
                        (bondpaper_left,),
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

                cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
                self.bondpaper_quantity = cursor.fetchone()[0]

                print(self.bondpaper_quantity)
    
    
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


class LoadingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(
            Qt.AlignCenter
        )  # Align progress bar in the center of its layout

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(
            0, 0
        )  # Set range to (0, 0) to make it an indeterminate progress bar
        self.progress_bar.setMaximumWidth(500)  # Set maximum width of the progress bar

        # Customize the progress bar style
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: #EBEBEB;
            }
            QProgressBar::chunk {
                background-color: #7C2F3E;
                width: 20px;
            }
            """
        )

        layout.addWidget(self.progress_bar)

        self.startLoading()  # Automatically start loading

        self.setLayout(layout)

    def startLoading(self):
        # Simulate loading by periodically updating the progress bar value
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateProgressBar)
        self.timer.start(100)  # Update every 100 milliseconds

    def updateProgressBar(self):
        # Increase progress bar value
        value = self.progress_bar.value() + 1
        if value > 100:
            value = 0  # Reset progress bar value
        self.progress_bar.setValue(value)
