import sys
import cups
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox

class PrinterStatusWorker(QThread):
    status_updated = pyqtSignal(bool, str)  # Signal to communicate printer status
    
    def __init__(self):
        super().__init__()
        self.printer_state = False
        self.running = True  # Control the running state of the thread

    def run(self):
        while self.running:
            self.is_printer_available()
            time.sleep(10)  # Check every 10 seconds

    def is_printer_available(self):
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()

            if not printers:
                self.printer_state = False
                raise Exception("No printers available.")

            idle_printer_found = False
            for printer_name, printer_attributes in printers.items():
                if (
                    "printer-state" in printer_attributes
                    and printer_attributes["printer-state"] == 3
                ):
                    idle_printer_found = True
                    self.printer_state = True
                    break

            if not idle_printer_found:
                self.printer_state = False
                raise Exception("No idle printer available")

            self.status_updated.emit(self.printer_state, "Idle printer found.")
        except Exception as e:
            self.printer_state = False
            self.status_updated.emit(self.printer_state, f"Error during printing: {e}")

    def stop(self):
        self.running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.worker = PrinterStatusWorker()
        self.worker.status_updated.connect(self.update_status_label)

    def initUI(self):
        self.label = QLabel("Press the button to start checking printer status", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.button = QPushButton("Start Checking", self)
        self.button.clicked.connect(self.toggle_checking)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setWindowTitle('Printer Status Checker')
        self.setGeometry(300, 300, 400, 200)
    
    def toggle_checking(self):
        if self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()  # Ensure the thread is completely stopped
            self.button.setText("Start Checking")
            self.label.setText("Checking stopped.")
        else:
            self.worker.start()
            self.button.setText("Stop Checking")
            self.label.setText("Checking printer status...")

    @pyqtSlot(bool, str)
    def update_status_label(self, status, message):
        self.label.setText(message)

    def closeEvent(self, event):
        if self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
