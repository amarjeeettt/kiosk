from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal


class CustomMessageBox(QDialog):
    button_clicked = pyqtSignal()

    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Message Box")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()
        self.setLayout(layout)

        message_label = QLabel(message)
        layout.addWidget(message_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok_button_clicked)
        button_layout.addWidget(ok_button, alignment=Qt.AlignCenter)

    def on_ok_button_clicked(self):
        self.button_clicked.emit()
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.show_message_box_button = QPushButton("Show Message Box")
        self.show_message_box_button.clicked.connect(self.show_message_box)
        layout.addWidget(self.show_message_box_button, alignment=Qt.AlignCenter)

    def show_message_box(self):
        message_box = CustomMessageBox("Hello", parent=self)
        message_box.exec_()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
