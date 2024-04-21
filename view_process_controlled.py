from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal

class ViewProcessControlledWindow(QMainWindow):
    view_form_backbt_clicked = pyqtSignal()
    
    def __init__(self, label):
        super().__init__()

        # Set window size
        self.showMaximized()

        # Create a central widget for the window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a label to display some text in the window
        label = QLabel(label)
        label.setAlignment(Qt.AlignCenter)  # Align text to the center
        
        self.back_bt = QPushButton("Back", self)
        self.back_bt.setGeometry(0, 40, 120, 95)  # (x, y, width, height)
        self.back_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #A93F55; 
                color: #F3F7F0; 
                font-family: Montserrat;
                font-size: 24px; 
                font-weight: bold; 
                letter-spacing: 3px;
                border-top-right-radius: 40px;
                border-bottom-right-radius: 40px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border: none;
                padding-right: 15px;
            }
            QPushButton:pressed {
                color: #D8C995;
            }
            """
        )
        self.back_bt.setFocusPolicy(Qt.NoFocus)
        self.back_bt.clicked.connect(self.go_back)
        self.back_bt.show()
        
        layout.addWidget(label)
        
    def go_back(self):
        self.close()
        self.view_form_backbt_clicked.emit()