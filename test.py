"""
import time
from gpiozero import Button

coinslot = Button(22)

while True:
    coinslotState = True
    counter = 0
    while coinslotState:
            if coinslot.is_pressed:
                counter+=1
                time.sleep(.05)
                print(counter)
"""

from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QPixmap, QPainterPath
from PyQt5.QtCore import QSize, QRectF
import sys

class ImageButton(QPushButton):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)
        self.border_radius = 35  # Set the desired border radius here

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create a rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.border_radius, self.border_radius)
        
        # Clip the painting region to the rounded rectangle
        painter.setClipPath(path)
        
        # Draw the pixmap
        painter.drawPixmap(self.rect(), self.pixmap)
        
        # Draw the button text
        super().paintEvent(event)

    def sizeHint(self):
        return self.pixmap.size()

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()

        # Create a custom ImageButton
        btn = ImageButton('./img/background.jpg', self)
        btn.setText('Button Text')
        btn.setStyleSheet("""
            QPushButton {
                border: none; /* Remove border */
                color: white; /* Set text color */
                font-size: 16px; /* Set text size */
                border-radius: 35px;
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 50); /* Optional: add a slight overlay when pressed */
            }
        """)

        vbox.addWidget(btn)
        self.setLayout(vbox)

        self.setWindowTitle('Custom Button with Background Image and Border Radius')
        self.setGeometry(300, 300, 300, 200)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
