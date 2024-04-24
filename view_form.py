import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QWidget,
    QHBoxLayout,
    QDesktopWidget,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from print_preview import PrintPreviewWindow
from view_process_controlled import ViewProcessControlledWindow


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
            self.verticalScrollBar().setValue(
                self._scrollBarValueAtMousePress - delta.y()
            )
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

        self.set_background_image()
        self.showMaximized()  # Increased width to accommodate more buttons

        # connect database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        self.coins_left = cursor.fetchone()[0]

        cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
        self.bondpaper_quantity = cursor.fetchone()[0]

        conn.close()

        main_layout = QVBoxLayout()

        # Adding back button and labels in top right corner
        top_layout = QHBoxLayout()

        # Add back button to the layout
        back_button_layout = QHBoxLayout()
        self.back_bt = QPushButton("Back")
        self.back_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E; 
                color: #FAEBD7; 
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
                background-color: #D8973C;
            }
            """
        )
        self.back_bt.setFocusPolicy(Qt.NoFocus)
        self.back_bt.clicked.connect(self.go_back)
        back_button_layout.addWidget(self.back_bt, alignment=Qt.AlignLeft)
        top_layout.addLayout(back_button_layout)

        # Adding labels in top right corner
        top_right_layout = QHBoxLayout()
        label1 = QLabel(f"Bondpaper Left: {self.bondpaper_quantity}")
        label2 = QLabel(f"Coins Left: {self.coins_left}")
        top_right_layout.addWidget(label1, alignment=Qt.AlignRight)
        top_right_layout.addWidget(label2, alignment=Qt.AlignRight)
        top_right_layout.setSpacing(0)
        top_right_layout.setContentsMargins(0, 0, 130, 0)
        top_layout.addLayout(top_right_layout)

        main_layout.addLayout(top_layout)

        button_labels = {
            "form_names": [
                "Individual Request of Petition Subject",
                "Consolidated Requests of Petition Subject",
                "Request on Shifting of Course",
                "Thesis Distribution Form",
                "Application for Subject Accreditation",
                "Evaluation of Graduating Student with Academic Honors",
                "List of Graduating Students with Academic Honors",
                "List of Graduating Students with Loyalty Award",
                "List of Graduating Students with Recognition Award",
                "Form 1",
                "Form 2",
                "Form 3",
                "Form 4",
                "Form 5",
                "Form 6",
                "Form 7",
                "Form 8",
                "Form 9",
            ],
            "form_types": [
                "Uncontrolled",
                "Uncontrolled",
                "Uncontrolled",
                "Uncontrolled",
                "Uncontrolled",
                "Uncontrolled",
                "Uncontrolled",
                "Uncontrolled",
                "Uncontrolled",
                "Controlled",
                "Controlled",
                "Controlled",
                "Controlled",
                "Controlled",
                "Controlled",
                "Controlled",
                "Controlled",
                "Controlled",
            ],
            "num_of_page": [2, 1, 1, 1, 1, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        }

        num_buttons = len(button_labels["form_names"])
        num_columns = 5
        num_rows = (
            num_buttons + num_columns - 1
        ) // num_columns  # Calculate the number of rows

        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QGridLayout(scroll_widget)

        # Set spacing between buttons
        scroll_layout.setHorizontalSpacing(20)
        scroll_layout.setVerticalSpacing(50)

        for i, label_text in enumerate(button_labels["form_names"]):
            row = i // num_columns
            col = i % num_columns
            button = QPushButton()
            button.setFixedSize(250, 250)
            button_layout = QVBoxLayout(button)
            button.setStyleSheet(
                """
                QPushButton {
                    border-radius: 45px;
                    background-color: #7C2F3E;
                    color: #F3F7F0;
                    padding-bottom: 50px;
                    text-align: bottom;  /* Align text to the bottom */
                }
                QPushButton:pressed {
                    background-color: #D8973C;
                }
                """
            )

            button.clicked.connect(
                lambda _, label=label_text: self.open_button_window(
                    label, button_labels
                )
            )

            # Create QLabel for the image
            image_label = QLabel()
            icon = QIcon("./img/view_forms_icon.svg")
            pixmap = icon.pixmap(QSize(200, 200))
            pixmap = pixmap.scaled(
                QSize(100, 100), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )  # Adjust size as needed
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("margin-top: 45px;")
            button_layout.addWidget(image_label)

            label = QLabel(label_text)
            label.setAlignment(Qt.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet(
                """
                QLabel {
                    font-family: Montserrat;
                    font-size: 11px; 
                    font-weight: bold; 
                    padding: 0px 25px 0px 25px; /* Adjust padding as needed */
                    background-color: transparent;
                    margin-bottom: 25px;
                    color: #FAEBD7;
                    }
                """
            )
            button_layout.addWidget(label)

            scroll_layout.addWidget(button, row, col)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(
            min(num_rows, 3) * 230 + 20
        )  # Maximum of 3 rows of buttons + spacing, smaller height
        scroll_area.setStyleSheet(
            """
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
                background-color: #7B0323;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #7B0323;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
            }
            """
        )
        main_layout.addWidget(scroll_area)

        # Set window layout
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def set_background_image(self):
        # Get screen resolution
        screen_resolution = QDesktopWidget().screenGeometry()

        # Load the background image
        pixmap = QPixmap("./img/background.jpg")

        # Resize the background image to fit the screen resolution
        pixmap = pixmap.scaled(screen_resolution.width(), screen_resolution.height())

        # Create a label to display the background image
        background_label = QLabel(self)
        background_label.setPixmap(pixmap)
        background_label.setGeometry(
            0, 0, screen_resolution.width(), screen_resolution.height()
        )  # Set label size to screen resolution
        background_label.setScaledContents(True)

    # Slot to handle going back to the main window
    def go_back(self):
        self.setVisible(False)
        self.home_screen_backbt_clicked.emit()

    def open_button_window(self, label, button_labels):
        form_names = button_labels["form_names"]
        form_types = button_labels["form_types"]

        try:
            index = form_names.index(label)
            form_type = form_types[index]
            num_of_pages = button_labels["num_of_page"][index]

            print(
                f"Button label '{label}' clicked, Form Type: {form_type}, Number of Pages: {num_of_pages}"
            )

            if form_type == "Uncontrolled":
                self.new_window = PrintPreviewWindow(label, num_of_pages)
                self.new_window.setVisible(True)
                self.setVisible(False)

                self.new_window.view_form_backbt_clicked.connect(
                    self.go_back_to_view_form
                )
            else:
                self.new_window = ViewProcessControlledWindow(label)
                self.new_window.setVisible(True)
                self.setVisible(False)

                self.new_window.view_form_backbt_clicked.connect(
                    self.go_back_to_view_form
                )
        except ValueError:
            print(f"Label '{label}' not found in the form names.")

    def go_back_to_view_form(self):
        self.setVisible(False)
        self.show()
