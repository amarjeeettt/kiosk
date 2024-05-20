import sys
from PyQt5.QtWidgets import QApplication, QLabel, QSlider, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QImage, QPixmap

class ImageZoomWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.image = QImage('./img/process/map.jpg').scaled(
            1440, 900, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.zoom_level = 1.0
        self.offset = QPoint(0, 0)
        self.last_mouse_pos = QPoint(0, 0)
        self.panning = False

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.update_image_display()

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.zoom_image)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.zoom_slider)
        self.setLayout(layout)

    def zoom_image(self):
        old_zoom_level = self.zoom_level
        zoom_percent = self.zoom_slider.value()
        self.zoom_level = zoom_percent / 100.0

        # Adjust the offset to zoom towards the center
        if self.zoom_level > old_zoom_level:
            self.offset.setX(self.offset.x() + int((self.image.width() * (self.zoom_level - old_zoom_level)) / 2))
            self.offset.setY(self.offset.y() + int((self.image.height() * (self.zoom_level - old_zoom_level)) / 2))
        else:
            self.offset.setX(self.offset.x() - int((self.image.width() * (old_zoom_level - self.zoom_level)) / 2))
            self.offset.setY(self.offset.y() - int((self.image.height() * (old_zoom_level - self.zoom_level)) / 2))
        
        self.update_image_display()

    def update_image_display(self):
        new_width = int(self.image.width() * self.zoom_level)
        new_height = int(self.image.height() * self.zoom_level)
        
        self.offset.setX(max(0, min(self.offset.x(), self.image.width() - new_width)))
        self.offset.setY(max(0, min(self.offset.y(), self.image.height() - new_height)))
        
        visible_image = self.image.copy(
            self.offset.x(), self.offset.y(),
            min(new_width, self.image.width() - self.offset.x()),
            min(new_height, self.image.height() - self.offset.y())
        ).scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio
        )
        
        self.image_label.setPixmap(QPixmap.fromImage(visible_image))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.panning = True
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.pos() - self.last_mouse_pos
            self.offset -= delta
            self.offset.setX(max(0, min(self.offset.x(), self.image.width() - int(self.image.width() * self.zoom_level))))
            self.offset.setY(max(0, min(self.offset.y(), self.image.height() - int(self.image.height() * self.zoom_level))))
            self.last_mouse_pos = event.pos()
            self.update_image_display()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.panning = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageZoomWidget()
    window.show()
    sys.exit(app.exec_())
