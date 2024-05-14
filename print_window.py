import cups
import sqlite3
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QProgressBar,
)
from PyQt5.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie, QPainter, QColor, QPen



class PrintMessageBox(QDialog):
    def __init__(self, title, num_copy, num_pages, total, is_total_equal, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 900)
        self.setStyleSheet("background-color: #EBEBEB;")

        self.setup_ui(title, num_copy, num_pages, total, is_total_equal)

    def setup_ui(self, title, num_copy, num_pages, total, is_total_equal):
        self.layout = QVBoxLayout(self)

        self.title = title
        self.num_copy = num_copy
        self.num_pages = num_pages
        self.total = total

        if is_total_equal == True:
            self.create_print_widget()
        else:
            self.warning_print_widget = WarningPrint(self)
            self.warning_print_widget.cancel_bt_clicked.connect(self.cancel_bt)
            self.warning_print_widget.ok_button_clicked.connect(
                self.create_print_widget
            )
            self.layout.addWidget(self.warning_print_widget)

    def cancel_bt(self):
        self.reject()

    def create_print_widget(self):
        self.print_progress_widget = PrintInProgress(self, self.title, self.num_copy, self.num_pages, self.total)
        self.layout.addWidget(self.print_progress_widget)


class PrintInProgress(QWidget):
    def __init__(self, parent, title, num_copy, num_pages, total):
        super().__init__(parent)
        self.setup_ui(title, num_copy, num_pages, total)
        self.print_result = None

    def setup_ui(self, title, num_copy, num_pages, total):
        layout = QVBoxLayout(self)
        layout.addSpacerItem(
            QSpacerItem(20, 85, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        self.gif_label = QLabel()
        self.movie = QMovie("./img/animated_printer.gif")
        self.gif_label.setMovie(self.movie)
        self.movie.start()
        layout.addWidget(self.gif_label)

        self.message_title = QLabel("Printing in Progress")
        self.message_title.setAlignment(Qt.AlignCenter)
        self.message_title.setStyleSheet(
            """
            font-size: 18px; 
            font-family: Open Sans; 
            font-weight: bold; 
            color: #19323C; 
            margin-bottom: 10px; 
            """
        )
        layout.addWidget(self.message_title)

        self.loading_widget = LoadingWidget()
        self.loading_widget.setContentsMargins(0, 0, 0, 5)
        layout.addWidget(self.loading_widget)

        self.message_label = QLabel("Please wait for a moment.")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet(
            """
            font-size: 14px; 
            font-family: Open Sans; 
            text-align: center; 
            padding-left: 30px; 
            padding-right: 30px; 
            margin-bottom: 160px;
            """
        )
        layout.addWidget(self.message_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)
        self.timer.start(500)
        
        QTimer.singleShot(3000, lambda: self.print_document(title, num_copy, num_pages, total))
        
    
    def print_document(self, title, num_copy, num_pages, total):
        bondpaper_left = num_copy * num_pages
        
        try: 
            conn = cups.Connection()
            printers = conn.getPrinters()
            
            if not printers:
                raise Exception('No Printers Available.')
            
            printer_name = list(printers.keys())[0]
            
            printer_attributes = conn.getPrinterAttributes(printer_name)
            if 'printer-state' not in printer_attributes or printer_attributes['printer-state'] != 3:
                raise Exception('Printer is not connected or offline.')
            
            file_path = f"./forms/{title}.pdf"
            
            # Define printer options (media)
            printer_options = {
                "media": "legal",  # Set media to legal size
            }

            for _ in range(num_copy):
                try:
                    job_id = conn.printFile(
                        printer_name, file_path, "Print Job", printer_options
                    )
                    print("Print job submitted with ID:", job_id)
                    
                    if self.check_print_job_status(job_id):
                        self.print_result = "Success"
                    else:
                        self.print_result = "Failed"
                        break
                    
                except (cups.IPPError, cups.ServerError, cups.IPPConnectionError) as e:
                    self.print_result = "Failed"
                    raise Exception(e)

        except Exception as e:
            print("Error during printing:", e)
            self.print_result = "Failed"

        finally:
            conn = None
            formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

            with sqlite3.connect("kiosk.db") as conn_sqlite:
                cursor = conn_sqlite.cursor()

                if self.print_result == 'Success':
                    cursor.execute(
                        "UPDATE kiosk_settings SET bondpaper_quantity = bondpaper_quantity - ?, coins_left = 0", 
                        (bondpaper_left,),
                    )
                    self.print_success()
                else:
                    self.print_failed()

                cursor.execute(
                    "INSERT INTO kiosk_print_results (date_printed, form_name, number_of_copies, total_amount, result) VALUES (?, ?, ?, ?, ?)",
                    (
                        formatted_datetime,
                        title,
                        num_copy,
                        total,
                        self.print_result,
                    ),
                )
                conn_sqlite.commit()

                cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
                self.bondpaper_quantity = cursor.fetchone()[0]

                print(self.bondpaper_quantity)
    
    def check_print_job_status(self, job_id):
        try:
            completed_jobs = subprocess.check_output(["lpstat", "-W", "completed", "-o"]).decode("utf-8")
            if job_id in completed_jobs:
                print(f"Print job with ID {job_id} was successful!")
                return True
            else:
                print(f"Print job with ID {job_id} was not found or encountered an error.")
                return False
        except subprocess.CalledProcessError as e:
            print("Error executing lpstat command:", e)
            return False
    
    def print_success(self):
        self.movie.stop()
        pixmap = QPixmap("./img/static/print_success.png")
        pixmap = pixmap.scaledToWidth(
            256, Qt.SmoothTransformation
        )
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setPixmap(pixmap)
        
        self.message_title.setText('Printed Successfully')
        self.loading_widget.hide()
        self.message_label.setText('Returning to home screen.')
        
        #QTimer.singleShot()
    
    def print_failed(self):
        self.movie.stop()
        pixmap = QPixmap("./img/static/print_failed.png")
        pixmap = pixmap.scaledToWidth(
            256, Qt.SmoothTransformation
        )
        self.gif_label.setAlignment(Qt.AlignCenter) 
        self.gif_label.setPixmap(pixmap)
        
        self.message_title.setText('Failed to Print')
        self.loading_widget.hide()
        self.message_label.setText('Returning to home screen.')
        
        #QTimer.singleShot()
    
    
    def update_label(self):
        text = self.message_label.text()
        if text.endswith("...."):
            text = text[:-4]  # Remove the last four characters
        else:
            text += "."  # Add a period
        self.message_label.setText(text)

class WarningPrint(QWidget):
    cancel_bt_clicked = pyqtSignal()
    ok_button_clicked = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.layout.addSpacerItem(
            QSpacerItem(20, 105, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        self.circle_loading = CircularLoadingWidget()
        self.layout.addWidget(self.circle_loading, alignment=Qt.AlignCenter)
        self.circle_loading.hide()

        self.image_label = QLabel()
        pixmap = QPixmap("./img/static/warning.png")
        pixmap = pixmap.scaledToWidth(
            256, Qt.SmoothTransformation
        )  # Scale the image width to fit the label
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.title_label = QLabel("Warning")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            """
            font-size: 32px; 
            font-family: Montserrat; 
            font-weight: bold; 
            color: #19323C;
            """
        )
        self.layout.addWidget(self.title_label)

        self.message_title = QLabel("Exceeded Total Coins Inserted")
        self.message_title.setAlignment(Qt.AlignCenter)
        self.message_title.setStyleSheet(
            """
            font-size: 18px; 
            font-family: Open Sans; 
            font-weight: bold; 
            color: #19323C; 
            margin-bottom: 40px; 
            """
        )
        self.layout.addWidget(self.message_title)

        self.message_label = QLabel(
            "It appears you have inserted more coins than necessary. If you continue, the excess coins will not be returned.\n\nPlease press confirm if you wish to proceed."
        )
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet(
            """
            font-size: 14px; 
            font-family: Open Sans; 
            text-align: center; 
            padding-left: 30px; 
            padding-right: 30px; 
            margin-bottom: 60px;
            """
        )
        self.layout.addWidget(self.message_label)

        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(165, 65)
        self.cancel_button.clicked.connect(lambda: self.cancel_bt_clicked.emit())
        self.cancel_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border-radius: 5px;
                color: #FAEBD7; 
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )

        self.ok_button = QPushButton("Confirm")
        self.ok_button.setFixedSize(165, 65)
        self.ok_button.clicked.connect(self.on_ok_button_clicked)
        self.ok_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border-radius: 5px;
                color: #FAEBD7; 
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        button_layout.setContentsMargins(70, 0, 70, 100)

        self.layout.addLayout(button_layout)

    def on_ok_button_clicked(self):
        # Hide all other widgets except the circular loading widget
        self.image_label.hide()
        self.title_label.hide()
        self.message_title.hide()
        self.message_label.hide()
        self.cancel_button.hide()
        self.ok_button.hide()

        self.circle_loading.show()
        QTimer.singleShot(3000, self.hide_loading_widget)

    def hide_loading_widget(self):
        self.hide()
        self.ok_button_clicked.emit()


class CircularLoadingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAngle)
        self.timer.start(30)  # Update every 30 milliseconds

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        # Set up circular loading widget
        self.setFixedSize(250, 250)  # Set minimum size

    def updateAngle(self):
        self.angle += 5
        self.angle %= 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set up pen and brush
        pen = QPen(QColor("#7C2F3E"))  # Set color to #7C2F3E
        pen.setWidth(15)  # Increase the width to make it thicker
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Calculate center and radius
        center = self.rect().center()
        radius = min(self.width(), self.height()) / 4

        # Draw the circular loading indicator
        arc_rect = QRectF(
            center.x() - radius, center.y() - radius, 2 * radius, 2 * radius
        )
        start_angle = (self.angle - 90) * 16
        span_angle = 60 * 16
        painter.drawArc(arc_rect, start_angle, span_angle)


class LoadingWidget(QWidget):
    def __init__(self):
        super().__init__()

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

        layout = QVBoxLayout(self)
        layout.setAlignment(
            Qt.AlignCenter
        )  # Align progress bar in the center of its layout
        layout.addWidget(self.progress_bar)