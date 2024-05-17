import sqlite3
from PyQt5.QtWidgets import (
    QPushButton,
    QGridLayout,
    QFrame,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QWidget,
    QHBoxLayout,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QSpacerItem,
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSignal


class SmoothScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalScrollBar().setSingleStep(15)  # Set the scrolling step size
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


class ButtonWidget(QWidget):
    # Define a new signal
    buttonClicked = pyqtSignal(str, str)

    def __init__(self, title_label, page_number_label, description_label, category):
        super().__init__()
        self.title_text = title_label
        self.page_number_text = page_number_label
        self.description_text = description_label
        self.category = category

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create a QFrame to contain the labels and button
        self.frame = QFrame(self)
        # Apply shadow effect to the frame
        self.applyShadowEffect()

        # Labels
        self.title_label = QLabel(self.title_text)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(
            """
                font-family: Montserrat;
                font-size: 19px;
                font-weight: bold;
                padding-top: 15px;
                padding-left: 15px;
                padding-right: 15px;
                color: #7C2F3E;
            """
        )

        self.num_pages_layout = QHBoxLayout()

        self.bondpaper_img = QLabel()
        self.pixmap = QPixmap("./img/static/paper_img.png")
        self.bondpaper_img.setPixmap(self.pixmap)

        self.page_number_label = QLabel(self.page_number_text)

        self.num_pages_layout.addWidget(self.bondpaper_img)
        self.num_pages_layout.addWidget(self.page_number_label)

        self.num_pages_layout.setContentsMargins(15, 0, 180, 0)

        self.description_label = QLabel(self.description_text)
        self.description_label.setStyleSheet(
            """
            font-family: Open Sans;
            font-size: 12px;
            """
        )
        self.description_label.setWordWrap(True)
        self.description_label.setContentsMargins(15, 0, 15, 0)

        # Button
        self.button = QPushButton("View")
        self.button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E; 
                color: #FAEBD7; 
                font-family: Montserrat;
                font-size: 16px; 
                font-weight: bold; 
                border-radius: 10px;
                border: none;
                margin-left: 25px;
                margin-right: 25px;
                margin-bottom: 15px;
                min-width: 150px;
                min-height: 70px;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        self.button.clicked.connect(self.emitButtonClickedSignal)

        # Add labels and button to the layout
        layout.addWidget(self.title_label)
        layout.addLayout(self.num_pages_layout)
        layout.addWidget(self.description_label)

        # Add vertical spacer
        spacer_item = QSpacerItem(20, 95, QSizePolicy.Minimum, QSizePolicy.Preferred)
        layout.addItem(spacer_item)

        layout.addWidget(self.button)

        # Set layout to the QFrame
        self.frame.setLayout(layout)

        # Set the main layout for the widget
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.frame)

    def applyShadowEffect(self):
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(30)
        shadow_effect.setColor(QColor(0, 0, 0, 150))
        shadow_effect.setOffset(0, 0)
        self.frame.setGraphicsEffect(shadow_effect)

    def emitButtonClickedSignal(self):
        # Emit the signal with necessary data
        self.buttonClicked.emit(self.title_label.text(), self.page_number_label.text())


class ViewFormWidget(QWidget):
    view_button_clicked = pyqtSignal(str, int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

        # Connect navigation buttons to their respective slots
        self.nav_btn_all.clicked.connect(self.filter_buttons_all)
        self.nav_btn_category1.clicked.connect(self.filter_buttons_category1)
        self.nav_btn_category2.clicked.connect(self.filter_buttons_category2)
        self.nav_btn_category3.clicked.connect(self.filter_buttons_category3)
        self.nav_btn_category4.clicked.connect(self.filter_buttons_category4)
        self.nav_btn_category5.clicked.connect(self.filter_buttons_category5)
        self.nav_btn_category6.clicked.connect(self.filter_buttons_category6)
        self.nav_btn_category7.clicked.connect(self.filter_buttons_category7)

        # Set the active button initially
        self.active_button = self.nav_btn_all
        self.update_button_styles()

    def setup_ui(self):
        # connect database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        self.coins_left = cursor.fetchone()[0]

        cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
        self.bondpaper_quantity = cursor.fetchone()[0]

        conn.close()

        layout = QVBoxLayout(self)

        # Adding labels in top right corner
        rectangle_layout = QHBoxLayout()

        rectangle = QFrame()
        rectangle.setFrameShape(QFrame.StyledPanel)
        rectangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        rectangle.setFixedSize(465, 65)
        rectangle.setStyleSheet(
            "QFrame { background-color: #FDFDFD; border-radius: 20px; }"
        )

        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(50)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 0)  # Adjust the shadow's offset as needed

        # Apply the effect to the rectangle
        rectangle.setGraphicsEffect(shadow_effect)

        rectangle_layout.addWidget(rectangle, alignment=Qt.AlignTop | Qt.AlignRight)
        rectangle_layout.setContentsMargins(0, 30, 60, 0)

        rectangle_inner_layout = QHBoxLayout()
        rectangle_inner_layout.setContentsMargins(30, 0, 15, 0)
        rectangle.setLayout(rectangle_inner_layout)

        # Create layouts for bondpaper, coins, and printer
        bondpaper_layout = QHBoxLayout()
        coins_layout = QHBoxLayout()
        printer_layout = QHBoxLayout()

        # Set spacing and margins for each layout if needed
        bondpaper_layout.setSpacing(15)
        coins_layout.setSpacing(15)
        printer_layout.setSpacing(15)

        # Set contents margins for each layout if needed
        bondpaper_layout.setContentsMargins(30, 0, 30, 0)
        bondpaper_layout.setContentsMargins(30, 0, 30, 0)
        coins_layout.setContentsMargins(30, 0, 30, 0)
        printer_layout.setContentsMargins(30, 0, 30, 0)

        # Bondpaper widgets
        bondpaper_img = QLabel()
        pixmap = QPixmap("./img/static/bondpaper_quantity.png")
        bondpaper_img.setPixmap(pixmap)
        bondpaper_label = QLabel(str(self.bondpaper_quantity))
        bondpaper_layout.addWidget(bondpaper_img)
        bondpaper_layout.addWidget(bondpaper_label)

        # Coins widgets
        coins_img = QLabel()
        pixmap = QPixmap("./img/static/coins_img.png")
        coins_img.setPixmap(pixmap)
        coins_label = QLabel(f"{self.coins_left:0.2f}")
        coins_layout.addWidget(coins_img)
        coins_layout.addWidget(coins_label)

        # Printer widgets
        printer_img = QLabel()
        pixmap = QPixmap("./img/static/printer_img.png")
        printer_img.setPixmap(pixmap)
        printer_status_symbol = QLabel("X")
        printer_layout.addWidget(printer_img)
        printer_layout.addWidget(printer_status_symbol)

        # Add layouts to the rectangle_inner_layout
        rectangle_inner_layout.addLayout(bondpaper_layout)
        rectangle_inner_layout.addLayout(coins_layout)
        rectangle_inner_layout.addLayout(printer_layout)

        layout.addLayout(rectangle_layout)

        self.nav_btn_all = QPushButton("All")
        self.nav_btn_category1 = QPushButton("Academic Recognition")
        self.nav_btn_category2 = QPushButton("Accreditation")
        self.nav_btn_category3 = QPushButton("Clearance")
        self.nav_btn_category4 = QPushButton("Enrollment")
        self.nav_btn_category5 = QPushButton("Graduation")
        self.nav_btn_category6 = QPushButton("Petition")
        self.nav_btn_category7 = QPushButton("Research")

        # Set size policy for navigation buttons to Fixed
        self.nav_btn_all.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category6.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category7.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.nav_layout = QHBoxLayout()
        self.nav_buttons = [
            self.nav_btn_all,
            self.nav_btn_category1,
            self.nav_btn_category2,
            self.nav_btn_category3,
            self.nav_btn_category4,
            self.nav_btn_category5,
            self.nav_btn_category6,
            self.nav_btn_category7,
        ]

        for button in self.nav_buttons:
            self.nav_layout.addWidget(button)

        # Apply common CSS style to navigation buttons
        nav_css = """
            QPushButton {
                font-family: Montserrat;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding-bottom: 8px;
            }
        """

        # Set style sheet for navigation bar buttons
        self.nav_btn_all.setStyleSheet(
            """
            QPushButton { 
                font-family: Montserrat; 
                font-size: 16px; 
                font-weight: bold; 
                border: none; 
                border-bottom: 2px solid #7C2F3E; 
                padding-bottom: 5px; 
            }
            """
        )
        self.nav_btn_category1.setStyleSheet(nav_css)
        self.nav_btn_category2.setStyleSheet(nav_css)
        self.nav_btn_category3.setStyleSheet(nav_css)
        self.nav_btn_category4.setStyleSheet(nav_css)
        self.nav_btn_category5.setStyleSheet(nav_css)
        self.nav_btn_category6.setStyleSheet(nav_css)
        self.nav_btn_category7.setStyleSheet(nav_css)

        # Align the navigation bar to the top
        self.nav_layout.setAlignment(Qt.AlignTop)
        self.nav_layout.setSpacing(40)
        self.nav_layout.setContentsMargins(80, 20, 0, 0)

        layout.addLayout(self.nav_layout)

        # Add ButtonWidgets
        button_labels = fetch_button_labels()

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)

        num_forms = len(button_labels["form_names"])
        num_columns = 4
        num_rows = (num_forms + num_columns - 1) // num_columns

        for i, (
            form_name,
            number_of_pages,
            form_description,
            form_category,
        ) in enumerate(
            zip(
                button_labels["form_names"],
                button_labels["num_of_pages"],
                button_labels["form_description"],
                button_labels["form_category"],
            )
        ):
            button_widget = ButtonWidget(
                form_name, str(number_of_pages), form_description, form_category
            )
            button_widget.setFixedHeight(450)
            button_widget.setFixedWidth(330)
            button_widget.setStyleSheet(
                """
                    background-color: #FFFFFF;
                    border-radius: 15px
                """
            )
            row = i // num_columns
            col = i % num_columns
            self.grid_layout.addWidget(button_widget, row, col)

            # Connect the buttonClicked signal to the handleButtonClicked slot
            button_widget.buttonClicked.connect(self.handleButtonClicked)

        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()  # Create a widget to hold the grid layout
        scroll_widget.setStyleSheet("background-color: transparent;")

        scroll_area_layout = QVBoxLayout(scroll_widget)
        scroll_area_layout.addLayout(self.grid_layout)
        scroll_area_layout.setContentsMargins(20, 20, 30, 0)

        scroll_area.setWidget(
            scroll_widget
        )  # Set the scroll widget as the scroll area's widget
        scroll_area.setStyleSheet(
            """
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            """
        )

        layout.addWidget(scroll_area)

    def update_button_styles(self):
        # Reset style for all buttons
        for button in self.nav_buttons:
            button.setStyleSheet(
                """
                QPushButton {
                    font-family: Montserrat;
                    font-size: 16px;
                    font-weight: bold;
                    border: none;
                    padding-bottom: 8px;
                }
            """
            )

        # Set active button style
        self.active_button.setStyleSheet(
            """
            QPushButton { 
                font-family: Montserrat; 
                font-size: 16px; 
                font-weight: bold; 
                border: none; 
                border-bottom: 2px solid #7C2F3E; 
                padding-bottom: 5px; 
            }
        """
        )

    def filter_buttons_all(self):
        self.active_button = self.nav_btn_all
        self.filter_buttons(None)  # Pass None to show all buttons
        self.update_button_styles()

    def filter_buttons_category1(self):
        self.active_button = self.nav_btn_category1
        self.filter_buttons("Academic Recognition")  # Filter by category
        self.update_button_styles()

    def filter_buttons_category2(self):
        self.active_button = self.nav_btn_category2
        self.filter_buttons("Accreditation")  # Filter by category
        self.update_button_styles()

    def filter_buttons_category3(self):
        self.active_button = self.nav_btn_category3
        self.filter_buttons("Clearance")  # Filter by category
        self.update_button_styles()

    def filter_buttons_category4(self):
        self.active_button = self.nav_btn_category4
        self.filter_buttons("Enrollment")  # Filter by category
        self.update_button_styles()

    def filter_buttons_category5(self):
        self.active_button = self.nav_btn_category5
        self.filter_buttons("Graduation")  # Filter by category
        self.update_button_styles()

    def filter_buttons_category6(self):
        self.active_button = self.nav_btn_category6
        self.filter_buttons("Petition")  # Filter by category
        self.update_button_styles()

    def filter_buttons_category7(self):
        self.active_button = self.nav_btn_category7
        self.filter_buttons("Research")  # Filter by category
        self.update_button_styles()

    def filter_buttons(self, category):
        visible_widgets = []  # Maintain a list of visible widgets
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if isinstance(item.widget(), ButtonWidget):
                widget = item.widget()
                if category is None or widget.category == category:
                    widget.show()
                    visible_widgets.append(widget)  # Add visible widgets to the list
                else:
                    widget.hide()

        # Calculate the number of columns based on the number of visible widgets
        num_visible_widgets = len(visible_widgets)
        num_columns = min(num_visible_widgets, self.grid_layout.columnCount())

        # Adjust the layout to accommodate the visible widgets
        row = 0
        col = 0
        for i, widget in enumerate(visible_widgets):
            if col >= num_columns:
                row += 1
                col = 0
            self.grid_layout.addWidget(widget, row, col)
            col += 1

        # If the number of visible widgets is less than or equal to 3, align the layout to the left
        if num_visible_widgets <= 3:
            self.grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.grid_layout.setContentsMargins(40, 0, 0, 0)
        else:
            self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
            self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.grid_layout.setHorizontalSpacing(60)

    # Function to handle the emitted signal
    def handleButtonClicked(self, title, page_number):
        print("Title:", title)
        print("Page number:", int(page_number))

        self.view_button_clicked.emit(title, int(page_number))


def fetch_button_labels():
    conn = sqlite3.connect("kiosk.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT form_name, number_of_pages, form_description, form_category FROM kiosk_forms"
    )
    rows = cursor.fetchall()

    conn.close()

    form_names = []
    num_of_pages = []
    form_description = []
    form_category = []

    for row in rows:
        form_names.append(row[0])
        num_of_pages.append(row[1])
        form_description.append(row[2])
        form_category.append(row[3])

    # Create a dictionary to store the lists
    button_labels = {
        "form_names": form_names,
        "num_of_pages": num_of_pages,
        "form_description": form_description,
        "form_category": form_category,
    }

    return button_labels
