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
    QDialog,
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer, QEvent, pyqtSignal


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


class WarningMessageBox(QDialog):
    return_bt_clicked = pyqtSignal()

    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 325)

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #EBEBEB;")

        title_label = QLabel("Warning")
        title_label.setStyleSheet(
            "font-size: 24px; font-family: Montserrat; font-weight: bold; color: #7C2F3E;"
        )
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            "font-size: 14px; font-family: Roboto; margin-left: 15px; margin-right: 15px"
        )
        layout.addWidget(message_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        return_button = QPushButton("Return")
        return_button.setFocusPolicy(Qt.NoFocus)
        return_button.setFixedSize(100, 45)
        return_button.clicked.connect(self.return_clicked)
        return_button.setStyleSheet(
            """
            QPushButton {
                background-color: #B3B3B3;
                border-radius: 10px;
                color: #19323C;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: Montserrat;
            }
            QPushButton:pressed {
                background-color: #7C2F3E;
                color: #FAEBD7;
            }
            """
        )
        button_layout.addWidget(return_button, alignment=Qt.AlignCenter)

        continue_button = QPushButton("Continue")
        continue_button.setFocusPolicy(Qt.NoFocus)
        continue_button.setFixedSize(100, 45)
        continue_button.clicked.connect(lambda: self.accept())
        continue_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border-radius: 10px;
                color: #FAEBD7;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: Montserrat;
            }
            QPushButton:pressed {
                background-color: #B3B3B3;
                color: #19323C;
            }
            """
        )
        button_layout.addWidget(continue_button, alignment=Qt.AlignCenter)
        button_layout.setContentsMargins(55, 0, 65, 0)

    def return_clicked(self):
        self.return_bt_clicked.emit()
        self.close()


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
        self.button.setFocusPolicy(Qt.NoFocus)
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
    view_button_clicked = pyqtSignal(str, int, bool, bool, bool)
    go_back_clicked = pyqtSignal()

    def __init__(self, parent, is_printer_available):
        super().__init__(parent)
        self.setup_ui(is_printer_available)

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

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(30000)
        self.inactivity_timer.timeout.connect(self.go_back)
        self.inactivity_timer.start()

        self.installEventFilter(self)

    def setup_ui(self, is_printer_available):
        # connect database
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        self.coins_left = cursor.fetchone()[0]

        cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
        self.bondpaper_quantity = cursor.fetchone()[0]

        cursor.execute("SELECT ink_level FROM kiosk_settings LIMIT 1")
        self.ink_level = cursor.fetchone()[0]

        conn.close()

        layout = QVBoxLayout(self)

        # Adding labels in top right corner
        rectangle_layout = QHBoxLayout()

        rectangle = QFrame()
        rectangle.setFrameShape(QFrame.StyledPanel)
        rectangle.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        rectangle.setFixedSize(525, 65)
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
        rectangle_layout.setContentsMargins(0, 25, 60, 0)

        rectangle_inner_layout = QHBoxLayout()
        rectangle_inner_layout.setContentsMargins(25, 0, 15, 0)
        rectangle.setLayout(rectangle_inner_layout)

        # Create layouts for bondpaper, coins, printer, and ink
        bondpaper_layout = QHBoxLayout()
        coins_layout = QHBoxLayout()
        printer_layout = QHBoxLayout()
        ink_layout = QHBoxLayout()

        coins_layout.setContentsMargins(20, 0, 15, 0)

        # Bondpaper widgets
        self.bondpaper_warning = QPushButton("!")
        self.bondpaper_warning.setFocusPolicy(Qt.NoFocus)
        self.bondpaper_warning.setFixedSize(45, 45)
        self.bondpaper_warning.setStyleSheet(
            """
            QPushButton{
                font-weight: bold;
                font-size: 24px;
                background-color: #E2E2E2;
                color: #7C2F3E;
                border: none;
                border-radius: 15px;
            }
            QPushButton::pressed {
                color: #D8C995;
            }
            """
        )
        self.bondpaper_warning.clicked.connect(self.low_bondpaper)
        self.bondpaper_warning.hide()
        bondpaper_img = QLabel()
        pixmap = QPixmap("./img/static/bondpaper_quantity.png")
        bondpaper_img.setPixmap(pixmap)
        bondpaper_label = QLabel(str(self.bondpaper_quantity))
        bondpaper_layout.addWidget(self.bondpaper_warning)
        bondpaper_layout.addWidget(bondpaper_img)
        bondpaper_layout.addWidget(bondpaper_label, alignment=Qt.AlignLeft)

        # Coins widgets
        coins_img = QLabel()
        pixmap = QPixmap("./img/static/coins_img.png")
        coins_img.setPixmap(pixmap)
        coins_label = QLabel(f"{self.coins_left:0.2f}")
        coins_layout.addWidget(coins_img)
        coins_layout.addWidget(coins_label, alignment=Qt.AlignLeft)

        # Printer widgets
        self.printer_warning = QPushButton("!")
        self.printer_warning.setFocusPolicy(Qt.NoFocus)
        self.printer_warning.setFixedSize(45, 45)
        self.printer_warning.setStyleSheet(
            """
            QPushButton{
                font-weight: bold;
                font-size: 24px;
                background-color: #E2E2E2;
                color: #7C2F3E;
                border: none;
                border-radius: 15px;
            }
            QPushButton::pressed {
                color: #D8C995;
            }
            """
        )
        self.printer_warning.clicked.connect(self.printer_not_connected)
        self.printer_warning.hide()
        printer_img = QLabel()
        pixmap = QPixmap("./img/static/printer_img.png")
        printer_img.setPixmap(pixmap)
        self.printer_status_symbol = QLabel("✓")
        printer_layout.addWidget(self.printer_warning)
        printer_layout.addWidget(printer_img)
        printer_layout.addWidget(self.printer_status_symbol)

        # Ink Widgets
        self.ink_warning = QPushButton("!")
        self.ink_warning.setFocusPolicy(Qt.NoFocus)
        self.ink_warning.setFixedSize(45, 45)
        self.ink_warning.setStyleSheet(
            """
            QPushButton{
                font-weight: bold;
                font-size: 24px;
                background-color: #E2E2E2;
                color: #7C2F3E;
                border: none;
                border-radius: 15px;
            }
            QPushButton::pressed {
                color: #D8C995;
            }
            """
        )
        self.ink_warning.clicked.connect(self.low_ink)
        self.ink_warning.hide()
        ink_img = QLabel()
        pixmap = QPixmap("./img/static/ink_img.png")
        ink_img.setPixmap(pixmap)
        self.ink_status_symbol = QLabel("✓")
        ink_layout.addWidget(self.ink_warning)
        ink_layout.addWidget(ink_img)
        ink_layout.addWidget(self.ink_status_symbol)

        # Add layouts to the rectangle_inner_layout
        rectangle_inner_layout.addLayout(bondpaper_layout)
        rectangle_inner_layout.addLayout(coins_layout)
        rectangle_inner_layout.addLayout(printer_layout)
        rectangle_inner_layout.addLayout(ink_layout)

        layout.addLayout(rectangle_layout)

        self.is_printer_available = is_printer_available
        self.bondpaper_supply = True
        self.ink_supply = True

        if self.bondpaper_quantity <= 0:
            self.bondpaper_supply = False

        if self.ink_level <= 0:
            self.ink_supply = False
            self.printer_status_symol.setText("✕")

        if self.bondpaper_quantity <= 5:
            self.bondpaper_warning.show()

        if self.ink_level <= 75:
            self.ink_warning.show()

        if not is_printer_available:
            self.printer_warning.show()
            self.printer_status_symbol.setText("✕")

        self.nav_btn_all = QPushButton("All")
        self.nav_btn_all.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category1 = QPushButton("Academic Recognition")
        self.nav_btn_category1.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category2 = QPushButton("Accreditation")
        self.nav_btn_category2.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category3 = QPushButton("Clearance")
        self.nav_btn_category3.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category4 = QPushButton("Enrollment")
        self.nav_btn_category4.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category5 = QPushButton("Graduation")
        self.nav_btn_category5.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category6 = QPushButton("Petition")
        self.nav_btn_category6.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category7 = QPushButton("Research")
        self.nav_btn_category7.setFocusPolicy(Qt.NoFocus)

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

        self.inactivity_timer.stop()

        self.view_button_clicked.emit(
            title,
            int(page_number),
            self.is_printer_available,
            self.bondpaper_supply,
            self.ink_supply,
        )

    def printer_not_connected(self):
        self.printer_message_box = WarningMessageBox(
            "Uh-oh, it seems the printer is currently offline or not available. Please contact the admin staff for further assistance.\n\n\nWould you like to proceed or return to the menu?",
            parent=self,
        )
        self.printer_message_box.return_bt_clicked.connect(self.go_back)
        self.printer_message_box.exec_()

    def low_bondpaper(self):
        self.bondpaper_message_box = WarningMessageBox(
            "Uh-oh, it seems the bondpaper supply is low. Please contact the admin staff for further assistance.\n\n\nWould you like to proceed or return to the menu?",
            parent=self,
        )
        self.bondpaper_message_box.return_bt_clicked.connect(self.go_back)
        self.bondpaper_message_box.exec_()

    def low_ink(self):
        self.ink_message_box = WarningMessageBox(
            "Uh-oh, it seems the ink supply is low. Please contact the admin staff for further assistance.\n\n\nWould you like to proceed or return to the menu?",
            parent=self,
        )
        self.ink_message_box.return_bt_clicked.connect(self.go_back)
        self.ink_message_box.exec_()

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.MouseButtonPress, QEvent.KeyPress]:
            self.reset_inactivity_timer()
        return super().eventFilter(obj, event)

    def reset_inactivity_timer(self):
        self.inactivity_timer.start()

    def go_back(self):
        self.setVisible(False)
        self.inactivity_timer.stop()
        self.go_back_clicked.emit()


def fetch_button_labels():
    conn = sqlite3.connect("./database/kiosk.db")
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
