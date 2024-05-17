import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PyQt Restart Example")
        self.setGeometry(100, 100, 300, 200)

        button = QPushButton("Restart", self)
        button.clicked.connect(self.restart_application)

        layout = QVBoxLayout()
        layout.addWidget(button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def restart_application(self):
        """Restart the application."""
        # Save application state here if necessary
        QApplication.quit()  # Close the application
        # Execute the script again
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
