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
        
         # Add back button to the layout
        back_button_layout = QHBoxLayout()
        self.back_bt = QPushButton("Back")
        self.back_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #A93F55; 
                color: #F3F7F0; 
                font-family: Montserrat;
                font-size: 16px; 
                font-weight: bold; 
                border-radius: 10px;
                border: none;
                margin-left: 35px;
                min-width: 150px;
                min-height: 80px;
            }
            QPushButton:pressed {
                color: #D8C995;
            }
            """
        )
        self.back_bt.setFocusPolicy(Qt.NoFocus)
        self.back_bt.clicked.connect(self.go_back)
        back_button_layout.addWidget(self.back_bt, alignment=Qt.AlignLeft)
        layout.addLayout(back_button_layout)
        
        layout.addWidget(label)
        
    def go_back(self):
        self.close()
        self.view_form_backbt_clicked.emit()