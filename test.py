import sys
import time
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

from gpiozero import Button

class CoinCounter(QWidget):
    def __init__(self):
        super().__init__()

        self.counter = 0

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Coin Counter")
        layout = QVBoxLayout()

        self.label = QLabel("Coins inserted: 0")
        layout.addWidget(self.label)

        self.button = QPushButton("Exit")
        self.button.clicked.connect(self.close)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.counter_thread = CounterThread()
        self.counter_thread.counter_changed.connect(self.update_counter)
        self.counter_thread.start()

    def update_counter(self, counter):
        self.counter = counter
        self.label.setText(f"Coins inserted: {self.counter}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoinCounter()
    window.show()
    sys.exit(app.exec_())

