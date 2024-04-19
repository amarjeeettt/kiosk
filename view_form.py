import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QVBoxLayout, QScrollArea, QLabel, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from print_preview import PrintPreviewWindow
from view_process import ViewProcessWindow

class SmoothScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.verticalScrollBar().setSingleStep(20)  # Set the scrolling step size
        self._mousePressPos = None
        self._scrollBarValueAtMousePress = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressPos = event.globalPos()
            self._scrollBarValueAtMousePress = self.verticalScrollBar().value()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._mousePressPos:
            delta = event.globalPos() - self._mousePressPos
            self.verticalScrollBar().setValue(self._scrollBarValueAtMousePress - delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._mousePressPos = None
        self._scrollBarValueAtMousePress = None
        super().mouseReleaseEvent(event)

class ViewFormWindow(QMainWindow):
    # Define a signal for back button clicked
    home_screen_backbt_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.showMaximized()  # Increased width to accommodate more buttons

        main_layout = QVBoxLayout()

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
        main_layout.addLayout(back_button_layout)

        button_labels = ["Individual Request of Petition Subject", "Consolidated Requests of Petition Subject",
                         "Request on Shifting of Course", "Thesis Distribution Form",
                         "Application for Subject Accreditation", "Evaluation of Graduating Student with Academic Honors",
                         "List of Graduating Students with Academic Honors", "List of Graduating Students with Loyalty Award",
                         "List of Graduating Students with Recognition Award", "Form 1", "Form 2", "Form 3", "Form 4",
                         "Form 5", "Form 6", "Form 7", "Form 8", "Form 9", "Form 10", "Form 11", "Form 12"]

        num_buttons = len(button_labels)
        num_columns = 5
        num_rows = (num_buttons + num_columns - 1) // num_columns  # Calculate the number of rows

        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)

        # Set spacing between buttons
        scroll_layout.setHorizontalSpacing(20)
        scroll_layout.setVerticalSpacing(50)

        for i, label_text in enumerate(button_labels):
            row = i // num_columns
            col = i % num_columns
            button = QPushButton()
            button.setFixedSize(250, 250)
            button_layout = QVBoxLayout(button)
            button.setStyleSheet(
                '''
                QPushButton {
                    border: 3px solid #19323C;
                    border-radius: 45px;
                    background-color: #4CAF50;
                    color: white;
                    padding-bottom: 50px;
                    text-align: bottom;  /* Align text to the bottom */
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #1C6EA4;;
                    border: 2px solid #1C6EA4;
                }
                '''
            )

            button.clicked.connect(lambda _, label=label_text: self.open_button_window(label, button_labels))
            
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet(
                '''
                QLabel {
                    padding: 0px 25px 0px 25px; /* Adjust padding as needed */
                    background-color: transparent;
                    color: white;
                    }
                '''
            )
            button_layout.addWidget(label)
            
            scroll_layout.addWidget(button, row, col)
            
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(min(num_rows, 3) * 230 + 20)  # Maximum of 3 rows of buttons + spacing, smaller height
        scroll_area.setStyleSheet(
            '''
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background-color: transparent;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #A93F55;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #A93F55;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
            }
            '''
        )
        main_layout.addWidget(scroll_area)

        # Set window layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setStyleSheet("background-color: #F3F7F0;")

    # Slot to handle going back to the main window
    def go_back(self):
        self.close()
        self.home_screen_backbt_clicked.emit()


    def open_button_window(self, label, button_labels):
        index = button_labels.index(label)
        print(f"Button label '{label}' clicked, index: {index}")
        if index < 10:
            self.close()
            self.new_window = PrintPreviewWindow(label, index)
            self.new_window.show()
            
            self.new_window.view_form_backbt_clicked.connect(self.go_back_to_view_form)
        else:
            self.close()
            self.new_window = ViewProcessWindow(label)
            self.new_window.show()
            
            self.new_window.view_form_backbt_clicked.connect(self.go_back_to_view_form)
    
    
    def go_back_to_view_form(self):
        self.close()
        self.show()