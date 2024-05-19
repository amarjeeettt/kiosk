import sys
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QMovie

class PrinterStatusThread(QThread):
    status_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            status = self.check_printer_status()
            self.status_updated.emit(status)
            self.sleep(5)  # Check every 5 seconds

    def check_printer_status(self):
        # Simulate checking printer status
        import random
        statuses = ["Ready", "Printing", "Error"]
        return random.choice(statuses)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("Printer Status: Unknown", self)
        self.layout.addWidget(self.label)

        self.gif_label = QLabel(self)
        self.movie = QMovie("./img/animated_printer.gif")
        self.gif_label.setMovie(self.movie)
        self.layout.addWidget(self.gif_label)
        self.movie.start()

        self.status_thread = PrinterStatusThread()
        self.status_thread.status_updated.connect(self.update_status)
        self.status_thread.start()

    def update_status(self, status):
        self.label.setText(f"Printer Status: {status}")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
