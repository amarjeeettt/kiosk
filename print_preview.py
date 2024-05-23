import sqlite3
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QDialog,
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QBrush, QColor, QIcon
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QPoint,
    QPropertyAnimation,
    QSize,
)


class MessageBox(QDialog):
    ok_button_clicked = pyqtSignal()

    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #EBEBEB;")

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 24px; font-family: Montserrat; font-weight: bold; color: #7C2F3E;"
        )
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Add a vertical spacer item
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 14px; font-family: Roboto; ")
        layout.addWidget(message_label, alignment=Qt.AlignCenter)

        # Add a vertical spacer item
        layout.addSpacerItem(
            QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Add a vertical spacer item
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        ok_button = QPushButton("OK")
        ok_button.setFocusPolicy(Qt.NoFocus)
        ok_button.setFixedSize(125, 45)
        ok_button.clicked.connect(self.on_ok_button_clicked)
        ok_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border-radius: 5px;
                color: #FAEBD7; 
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        button_layout.addWidget(ok_button, alignment=Qt.AlignCenter)

    def on_ok_button_clicked(self):
        self.accept()
        self.ok_button_clicked.emit()


class PrintPreviewWidget(QWidget):
    view_form_backbt_clicked = pyqtSignal()
    timer_expired = pyqtSignal()
    view_process_clicked = pyqtSignal(str)
    print_form_clicked = pyqtSignal(str, int, int, int)

    def __init__(
        self,
        parent,
        title,
        page_number,
        printer_status,
        bondpaper_status,
        ink_status,
    ):
        super().__init__(parent)
        self.setup_ui(title, page_number, printer_status, bondpaper_status, ink_status)

        self.swiping = False

    def setup_ui(
        self, title, page_number, printer_status, bondpaper_status, ink_status
    ):
        # Connect database
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT base_price FROM kiosk_settings LIMIT 1")
        self.base_price = cursor.fetchone()[0]

        cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
        self.bondpaper_quantity = cursor.fetchone()[0]

        conn.close()

        self.title = title
        self.page_number = page_number

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 55, 0, 0)

        left_window = QWidget()
        left_window.setFixedWidth(330)
        left_layout = QVBoxLayout(left_window)  # Use QVBoxLayout
        left_layout.setAlignment(Qt.AlignTop)  # Align top
        back_bt = QPushButton("Back")
        back_bt.setFocusPolicy(Qt.NoFocus)
        back_bt.setFixedSize(200, 100)  # Set fixed size
        back_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E; 
                color: #FAEBD7; 
                font-family: Montserrat;
                font-size: 16px; 
                font-weight: bold; 
                border-radius: 10px;
                border: none;
                margin-left: 165px;
                margin-top: 20px;
                min-width: 150px;
                min-height: 80px;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        back_bt.setFocusPolicy(Qt.NoFocus)
        back_bt.clicked.connect(self.go_back)
        left_layout.addWidget(back_bt)

        # Center image
        self.index = 1

        # Load the image
        self.image = (
            QImage(f"./img/form-preview/{self.title}-{self.index}.jpg")
            .scaledToWidth(700, Qt.SmoothTransformation)
            .scaledToHeight(830, Qt.SmoothTransformation)
        )
        # Apply border radius to the image
        self.apply_border_radius()

        # Create a pixmap from the image
        pixmap = QPixmap.fromImage(self.image)
        self.center_image = QLabel()
        self.center_image.setPixmap(pixmap)
        self.center_image.setAlignment(Qt.AlignCenter)

        # Top margin label for center image
        top_margin_label = QLabel()
        top_margin_label.setFixedHeight(25)  # Set the height of the margin

        # Bottom label
        self.bottom_label = QLabel(f"{self.index}/{self.page_number}")
        self.bottom_label.setStyleSheet(
            """
                QLabel {
                    font-family: Montserrat;
                    font-size: 16px; 
                    font-weight: bold;
                    color: #19323C;
                    }
            """
        )
        self.bottom_label.setAlignment(Qt.AlignCenter)

        # Create a layout for center image and bottom label
        center_layout = QVBoxLayout()
        center_layout.addWidget(top_margin_label)  # Add margin above the image
        center_layout.addWidget(self.center_image)
        center_layout.addWidget(self.bottom_label)

        # Right label
        form_label = self.title
        right_label = QLabel(form_label)
        right_label.setFixedSize(380, 150)
        right_label.setAlignment(Qt.AlignCenter)
        right_label.setWordWrap(True)
        right_label.setStyleSheet(
            """
                QLabel {
                    font-family: Montserrat;
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #19323C;
                    }
            """
        )
        right_layout = QVBoxLayout()
        right_layout.addWidget(
            right_label, alignment=Qt.AlignCenter
        )  # Align label in center

        # Bottom square inside right_label layout
        square_frame = QFrame()
        square_frame.setStyleSheet("background-color: #FDFDFD; border-radius: 45px;")
        # Set the size of the square frame
        square_frame.setFixedSize(420, 360)
        square_frame.setFrameStyle(QFrame.Box)
        square_frame_layout = QVBoxLayout(square_frame)
        square_label = QLabel("Total:")
        square_label.setStyleSheet(
            """
                QLabel {
                    font-family: Roboto;
                    font-size: 16px; 
                    color: #19323C;
                    letter-spacing: 3px;
                    }
            """
        )

        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(50)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 8)

        # Apply the shadow effect to the square_frame
        square_frame.setGraphicsEffect(shadow_effect)

        square_frame_layout.setContentsMargins(0, 90, 0, 0)
        square_frame_layout.addWidget(
            square_label, alignment=Qt.AlignCenter
        )  # Align label in center

        self.total = self.base_price * self.page_number
        self.total_label = QLabel(
            f"₱{self.total:0.2f}"
        )  # Initialize total label with base price
        self.total_label.setStyleSheet(
            """
                QLabel {
                    font-family: Montserrat;
                    font-size: 64px; 
                    font-weight: bold;
                    margin-top: 15px; 
                    color: #7C2F3E;
                    letter-spacing: 3px;
                    }
            """
        )
        square_frame_layout.addWidget(
            self.total_label, alignment=Qt.AlignCenter
        )  # Align label in center
        square_layout = QHBoxLayout()  # Layout for buttons and label
        decrement_button = QPushButton("-")
        decrement_button.setFocusPolicy(Qt.NoFocus)
        decrement_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border: none;
                color: #FAEBD7;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:pressed {
                background-color: #D8C995;
                color: #7C2F3E;
            }
            """
        )
        decrement_button.setFixedSize(65, 65)

        increment_button = QPushButton("+")
        increment_button.setFocusPolicy(Qt.NoFocus)
        increment_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border: none;
                color: #FAEBD7;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:pressed {
                background-color: #D8C995;
                color: #7C2F3E;
            }
            """
        )
        increment_button.setFixedSize(65, 65)

        self.value = 1
        self.label_between_buttons = QLabel(str(self.value))
        self.label_between_buttons.setStyleSheet(
            """
                QLabel {
                    margin-top: 12px;
                    font-family: Montserrat;
                    font-size: 24px; 
                    font-weight: bold;
                    color: #19323C;
                    }
            """
        )
        decrement_button.clicked.connect(self.decrement_value)
        increment_button.clicked.connect(self.increment_value)

        # Set margin for the square layout
        square_layout.setContentsMargins(100, 40, 100, 40)  # right, top, left, bottom

        square_layout.addWidget(decrement_button, alignment=Qt.AlignCenter)
        square_layout.addWidget(
            self.label_between_buttons, alignment=Qt.AlignCenter
        )  # Align label at center
        square_layout.addWidget(increment_button, alignment=Qt.AlignCenter)
        square_frame_layout.addLayout(square_layout)
        right_layout.addWidget(square_frame)

        # Outer buttons
        view_process_bt = QPushButton()
        view_process_bt.setFocusPolicy(Qt.NoFocus)
        view_process_bt.setFixedSize(250, 150)  # Set fixed size
        view_process_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #D8C995;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 12px;
            }
            QPushButton:pressed {
                background-color: #F3F7F0;
            }
            """
        )
        view_process_bt.clicked.connect(lambda: self.process_bt_clicked(self.title))

        # Create layout for button
        process_button_layout = QVBoxLayout()

        # Add image to button
        process_image_label = QLabel()
        icon = QIcon("./img/view_process_icon.svg")
        pixmap = icon.pixmap(QSize(200, 200))
        pixmap = pixmap.scaled(
            QSize(50, 50), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )  # Adjust size as needed
        process_image_label.setPixmap(pixmap)
        process_image_label.setContentsMargins(0, 25, 0, 0)
        process_image_label.setAlignment(Qt.AlignCenter)
        process_button_layout.addWidget(process_image_label)

        # Add label to button
        process_label = QLabel("View Process")
        process_label.setStyleSheet(
            """
                QLabel {
                font-family: Montserrat;
                font-size: 16px; 
                font-weight: bold;
                margin-bottom: 10px;
                color: #19323C;
                }
            """
        )
        process_label.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        process_button_layout.addWidget(process_label)

        # Set button layout
        view_process_bt.setLayout(process_button_layout)

        self.print_bt = QPushButton()
        self.print_bt.setFocusPolicy(Qt.NoFocus)
        self.print_bt.setFixedSize(250, 150)  # Set fixed size
        self.print_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 12px;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            QPushButton:disabled {
                background-color: #C0C0C0;
            }
            """
        )
        self.print_bt.clicked.connect(
            lambda: self.print_form_bt_clicked(title, page_number)
        )

        # Create layout for button
        print_button_layout = QVBoxLayout()

        # Add image to button
        self.print_image_label = QLabel()
        icon = QIcon("./img/print_forms_icon.svg")
        pixmap = icon.pixmap(QSize(200, 200))
        pixmap = pixmap.scaled(
            QSize(50, 50), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )  # Adjust size as needed
        self.print_image_label.setPixmap(pixmap)
        self.print_image_label.setContentsMargins(0, 25, 0, 0)
        self.print_image_label.setAlignment(Qt.AlignCenter)
        print_button_layout.addWidget(self.print_image_label)

        # Add label to button
        self.print_label = QLabel("Print Forms")
        self.print_label.setStyleSheet(
            """
                QLabel {
                font-family: Montserrat;
                font-size: 16px; 
                font-weight: bold;
                margin-bottom: 10px;
                color: #FAEBD7;
                }
            """
        )
        self.print_label.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        print_button_layout.addWidget(self.print_label)

        # Set button layout
        self.print_bt.setLayout(print_button_layout)

        if not printer_status:
            self.disable_print_button()

        if not bondpaper_status:
            self.disable_print_button()

        if not ink_status:
            self.disable_print_button()

        # Add vertical spacer item between square frame and outer buttons
        spacer_vertical = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        right_layout.addItem(spacer_vertical)

        right_layout.addWidget(view_process_bt, alignment=Qt.AlignCenter)
        right_layout.addWidget(self.print_bt, alignment=Qt.AlignCenter)

        # Add spacer item between center image and right layout
        spacer_left = QSpacerItem(120, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        spacer_right = QSpacerItem(140, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)
        spacer = QSpacerItem(100, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        main_layout.addWidget(left_window)
        main_layout.addItem(spacer_left)
        main_layout.addLayout(center_layout)
        main_layout.addItem(spacer_right)

        # Add right_layout as a widget with alignment
        widget = QWidget()
        widget.setLayout(right_layout)
        main_layout.addWidget(
            widget, alignment=Qt.AlignTop | Qt.AlignCenter
        )  # Align right layout to top

        main_layout.addItem(spacer)

        # Variables for swipe detection
        self.start_pos = QPoint()
        self.end_pos = QPoint()

        # Enable swipe feature if num_of_pages is greater than 1
        if self.page_number <= 1:
            self.center_image.mousePressEvent = lambda event: None
            self.center_image.mouseReleaseEvent = lambda event: None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.center_image.underMouse():
                self.start_pos = event.pos()
                self.swiping = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.swiping:
            self.end_pos = event.pos()
            delta = self.end_pos - self.start_pos

            if delta.x() > 50:  # Swipe right
                self.slide_left()
            elif delta.x() < -50:  # Swipe left
                self.slide_right()

            self.swiping = False

    def detect_swipe(self):
        delta_x = self.end_pos.x() - self.start_pos.x()
        if delta_x > 100:
            self.slide_left()
        elif delta_x < -100:
            self.slide_right()

    def slide_left(self):
        animation = QPropertyAnimation(self.center_image, b"geometry")
        animation.setDuration(500)
        animation.setStartValue(self.center_image.geometry())
        new_geometry = self.center_image.geometry()
        new_geometry.moveLeft(-self.width())
        animation.setEndValue(new_geometry)
        animation.start()

        self.previous_image()

    def slide_right(self):
        animation = QPropertyAnimation(self.center_image, b"geometry")
        animation.setDuration(500)
        animation.setStartValue(self.center_image.geometry())
        new_geometry = self.center_image.geometry()
        new_geometry.moveLeft(self.width())
        animation.setEndValue(new_geometry)
        animation.start()

        self.next_image()

    def next_image(self):
        if self.index < self.page_number:
            self.index += 1
            self.update_image()
            self.update_bottom_label()

    def previous_image(self):
        if self.index > 0:
            self.index -= 1
            self.update_image()
            self.update_bottom_label()

    def update_image(self):
        # Load the image corresponding to the new index
        self.image = (
            QImage(f"./img/form-preview/{self.title}-{self.index}.jpg")
            .scaledToWidth(700, Qt.SmoothTransformation)
            .scaledToHeight(830, Qt.SmoothTransformation)
        )
        # Apply border radius to the image
        self.apply_border_radius()

        # Create a pixmap from the updated image
        pixmap = QPixmap.fromImage(self.image)
        self.center_image.setPixmap(pixmap)

    def update_bottom_label(self):
        self.bottom_label.setText(f"{self.index}/{self.page_number}")

    def increment_value(self):
        if self.value < self.bondpaper_quantity:
            self.value += 1
            self.label_between_buttons.setText(str(self.value))
            self.update_total_label()

        if self.value >= self.bondpaper_quantity:
            self.inactivity_timer.stop()

            message_box = MessageBox(
                "Error",
                "Uh-oh, it appears the bondpaper is insufficient to add more.",
                parent=self,
            )
            message_box.ok_button_clicked.connect(self.reset_inactivity_timer)
            message_box.exec_()

    def decrement_value(self):
        if self.value > 1:
            self.value -= 1
            self.label_between_buttons.setText(str(self.value))
            self.update_total_label()

    def update_total_label(self):
        self.total = (self.base_price * self.page_number) * self.value
        self.total_label.setText(f"₱{self.total:0.2f}")

    def apply_border_radius(self):
        # Create a mask image with the desired border radius
        mask = QImage(self.image.size(), QImage.Format_ARGB32)
        mask.fill(Qt.transparent)

        # Create a QPainter for the mask
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(QColor(Qt.white)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.image.rect(), 20, 20)
        painter.end()

        # Apply the mask to the image
        self.image.setAlphaChannel(mask)

    def disable_print_button(self):
        self.print_bt.setEnabled(False)
        disabled_icon = QIcon("./img/print_forms_icon_disabled.svg")
        pixmap = disabled_icon.pixmap(QSize(200, 200))
        pixmap = pixmap.scaled(
            QSize(50, 50), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )  # Adjust size as needed
        self.print_image_label.setPixmap(pixmap)
        self.print_label.setStyleSheet(
            """
                QLabel {
                font-family: Montserrat;
                font-size: 16px; 
                font-weight: bold;
                margin-bottom: 10px;
                color: #828282
                }
            """
        )

    def process_bt_clicked(self, title):
        self.view_process_clicked.emit(title)

    def print_form_bt_clicked(self, title, page_number):
        self.print_form_clicked.emit(
            title, int(self.value), page_number, int(self.total)
        )

    def go_back_home(self):
        self.setVisible(False)
        self.inactivity_timer.stop()
        self.timer_expired.emit()

    def go_back(self):
        self.setVisible(False)
        self.inactivity_timer.stop()
        self.view_form_backbt_clicked.emit()
