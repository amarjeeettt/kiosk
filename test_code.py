from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
import time
import cups

class PrinterStatus(QThread):
    status_updated = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.printer_state = None
        self.running = True

    def run(self):
        while self.running:
            self.is_printer_available()
            time.sleep(10)

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
                    break

            if idle_printer_found:
                self.printer_state = True
            else:
                self.printer_state = False

            self.status_updated.emit(self.printer_state)
        except Exception as e:
            print(e)

    def stop(self):
        self.running = False

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Printer Status")

        self.label = QLabel("Printer Status: Unknown")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.printer_status = PrinterStatus()
        self.printer_status.status_updated.connect(self.update_label)
        self.printer_status.start()

    def update_label(self, status):
        if status:
            self.label.setText("Printer Status: Idle")
        else:
            self.label.setText("Printer Status: Not Idle")

    def closeEvent(self, event):
        self.printer_status.stop()
        self.printer_status.wait()
        event.accept()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
