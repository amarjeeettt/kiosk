from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QFrame, QLabel, QWidget, QHBoxLayout, QStackedWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient, QPainterPath
from PyQt5.QtCore import Qt, QSize,  QRectF

class InnerShadowFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define shadow properties
        shadow_color = QColor(0, 0, 0, 50)
        shadow_radius = 10

        # Draw inner shadow
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(0, 0, -shadow_radius, -shadow_radius), self.cornerRadius(), self.cornerRadius())
        painter.fillPath(path, QBrush(shadow_color))
        painter.setPen(QPen(shadow_color, shadow_radius))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(shadow_radius // 2, shadow_radius // 2, -shadow_radius, -shadow_radius), self.cornerRadius(), self.cornerRadius())

        # Draw content
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#FDFDFD"))  # Content color
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(shadow_radius, shadow_radius, -shadow_radius, -shadow_radius), self.cornerRadius(), self.cornerRadius())


        # Draw content
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#FDFDFD"))  # Content color
        painter.drawRoundedRect(self.rect().adjusted(shadow_radius, shadow_radius, -shadow_radius, -shadow_radius), self.cornerRadius(), self.cornerRadius())

    def cornerRadius(self):
        return 45  # Adjust as needed


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inner Shadow Frame Example")
        self.setGeometry(100, 100, 600, 400)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)

        # Add the inner shadow frame to the layout
        inner_shadow_frame = InnerShadowFrame()
        inner_shadow_frame.setObjectName("inner_shadow_frame")  # To apply specific style
        layout.addWidget(inner_shadow_frame, alignment=Qt.AlignCenter)

        # Add content inside the inner shadow frame
        content_layout = QVBoxLayout()
        inner_shadow_frame.setLayout(content_layout)

        label = QLabel("Inner Shadow Frame")
        label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(label)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
