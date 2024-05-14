import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QLabel, QWidget, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap

class CustomButton(QPushButton):
    def __init__(self, text, image_path, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()

        # Create label
        self.label = QLabel(text)

        # Load image
        pixmap = QPixmap(image_path)
        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap)

        # Create button
        #self.button = QPushButton()
        #self.button.setFixedSize(pixmap.width(), pixmap.height())

        # Add a spacer item
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        layout.addWidget(self.image_label)
        layout.addItem(spacer)
        layout.addWidget(self.label)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    button = CustomButton("Click me", "./img/static/dashboard.png")
    button.show()

    sys.exit(app.exec_())
