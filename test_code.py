import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame
from PyQt5.QtGui import QPixmap, QTransform, QPainter
from PyQt5.QtCore import Qt, QEvent

class PinchZoomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.viewport().setAttribute(Qt.WA_AcceptTouchEvents, True)
        self.setFrameShape(QFrame.NoFrame)
        self.scale_factor = 1.0

    def event(self, event):
        if event.type() == QEvent.TouchBegin or event.type() == QEvent.TouchUpdate:
            if len(event.touchPoints()) == 2:
                pinch = event.touchPoints()
                touch1 = pinch[0]
                touch2 = pinch[1]
                if touch1.state() == Qt.TouchPointPressed or touch2.state() == Qt.TouchPointPressed:
                    self.start_dist = (touch1.pos() - touch2.pos()).manhattanLength()
                    self.scale_factor = self.transform().m11()
                elif touch1.state() == Qt.TouchPointMoved or touch2.state() == Qt.TouchPointMoved:
                    current_dist = (touch1.pos() - touch2.pos()).manhattanLength()
                    scale = current_dist / self.start_dist
                    self.setTransform(QTransform().scale(self.scale_factor * scale, self.scale_factor * scale))
            return True
        return super().event(event)

class ImageZoomApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.main_view = PinchZoomGraphicsView()
        self.scene = QGraphicsScene(self.main_view)
        self.main_view.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem(QPixmap('./img/process/map.jpg'))  # Replace with your image path
        self.scene.addItem(self.pixmap_item)
        self.main_view.setSceneRect(self.pixmap_item.boundingRect())
        self.main_view.showFullScreen()

if __name__ == '__main__':
    app = ImageZoomApp(sys.argv)
    sys.exit(app.exec_())
