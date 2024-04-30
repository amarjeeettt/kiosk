import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        button = QPushButton("Click me", self)
        layout.addWidget(button)

        self.setWindowTitle("Mouse Event Example")

    def mousePressEvent(self, event):
        print("Mouse pressed at ({}, {})".format(event.x(), event.y()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
