import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QIcon, QPixmap

class FileExplorerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('File Explorer and Uploader')

        self.selected_file_label = QLabel("Selected File:", self)
        self.file_preview_label = QLabel(self)

        self.button_open = QPushButton('Open File Explorer', self)
        self.button_open.clicked.connect(self.openFileExplorer)

        self.button_upload = QPushButton('Upload File', self)
        self.button_upload.clicked.connect(self.uploadFile)
        self.button_upload.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.button_open)
        layout.addWidget(self.selected_file_label)
        layout.addWidget(self.file_preview_label)
        layout.addWidget(self.button_upload)

        self.setLayout(layout)

        self.show()

    def openFileExplorer(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # Use native dialog on macOS
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)", options=options)
        if file_path:
            print("Selected file:", file_path)
            self.displayFilePreview(file_path)
            self.selected_file_path = file_path
            self.button_upload.setEnabled(True)

    def displayFilePreview(self, file_path):
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            pixmap = QPixmap(file_path)
            self.file_preview_label.setPixmap(pixmap.scaledToWidth(200))
        else:
            # Use a default document icon
            icon_path = 'document_icon.png'  # Path to your document icon image
            pixmap = QPixmap(icon_path)
            self.file_preview_label.setPixmap(pixmap.scaledToWidth(64))  # Adjust the size as needed

    def uploadFile(self):
        # Upload the file to the current directory where the script is located
        destination_directory = './'
        if self.selected_file_path:
            file_name = os.path.basename(self.selected_file_path)
            destination_path = os.path.join(destination_directory, file_name)
            try:
                shutil.copy(self.selected_file_path, destination_path)
                print(f"File '{file_name}' uploaded to '{destination_directory}'")
            except Exception as e:
                print(f"Error uploading file: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileExplorerWindow()
    sys.exit(app.exec_())
