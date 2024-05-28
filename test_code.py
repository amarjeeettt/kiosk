import sys
import shutil
import os
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal

class CopyFileThread(QThread):
    file_copied = pyqtSignal()

    def __init__(self, source, destination):
        super().__init__()
        self.source = source
        self.destination = destination

    def run(self):
        shutil.copy(self.source, self.destination)
        self.file_copied.emit()

class CheckFileExistsThread(QThread):
    file_exists = pyqtSignal()
    file_not_found = pyqtSignal()

    def __init__(self, destination):
        super().__init__()
        self.destination = destination
        self.running = True

    def run(self):
        while self.running:
            if os.path.exists(self.destination):
                self.file_exists.emit()
                self.running = False
            else:
                self.file_not_found.emit()
            time.sleep(3)

    def stop(self):
        self.running = False

class FileCopyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        
        self.status_label = QLabel("Press the button to start copying the file.")
        self.layout.addWidget(self.status_label)

        self.copy_button = QPushButton("Start Copy")
        self.copy_button.clicked.connect(self.start_copy)
        self.layout.addWidget(self.copy_button)

        self.setLayout(self.layout)
        self.setWindowTitle('File Copy Status')
        self.show()

    def start_copy(self):
        self.status_label.setText("File uploading currently...")
        
        source_path = '/Users/amarjeetsingh/Downloads/slideshow.gif'
        destination_path = '/Users/amarjeetsingh/Desktop'

        self.copy_thread = CopyFileThread(source_path, destination_path)
        self.copy_thread.file_copied.connect(self.on_file_copied)
        self.copy_thread.start()

        self.check_thread = CheckFileExistsThread(destination_path)
        self.check_thread.file_exists.connect(self.on_file_exists)
        self.check_thread.file_not_found.connect(self.on_file_not_found)
        self.check_thread.start()

    def on_file_copied(self):
        self.status_label.setText("File copied finished.")

    def on_file_exists(self):
        self.status_label.setText("File is now at the destination.")
        self.check_thread.stop()

    def on_file_not_found(self):
        self.status_label.setText("File uploading currently...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileCopyApp()
    sys.exit(app.exec_())
