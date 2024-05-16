import os
import sqlite3
import datetime
from PyQt5.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QFrame,
    QGraphicsDropShadowEffect,
    QTabWidget,
    QAbstractScrollArea,
    QSpacerItem,
    QAbstractItemView,
    QScrollArea,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QFileDialog,
    QDialog,
    QMenu,
    QAction,
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPalette
from virtual_keyboard import AlphaNeumericVirtualKeyboard
from helpers import upload_form_file, upload_process_file
from custom_message_box import CustomMessageBox


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


class EditMessageBox(QDialog):
    edit_form_button_clicked = pyqtSignal(int, int, str)

    def __init__(self, index, form_name, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 325)

        self.index = index
        self.form_name = form_name

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #EBEBEB;")

        title_label = QLabel("Edit Form")
        title_label.setStyleSheet(
            "font-size: 24px; font-family: Montserrat; font-weight: bold; color: #7C2F3E;"
        )
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        message_label = QLabel(
            f"You're editing {form_name}.\n\nDo you want to continue making changes or discard."
        )
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 14px; font-family: Roboto; ")
        layout.addWidget(message_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        file_button = QPushButton("Discard")
        file_button.setFixedSize(100, 45)
        file_button.clicked.connect(lambda: self.reject())
        file_button.setStyleSheet(
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
        button_layout.addWidget(file_button, alignment=Qt.AlignCenter)

        form_file_button = QPushButton("Continue")
        form_file_button.setFixedSize(100, 45)
        form_file_button.clicked.connect(self.edit_form_clicked)
        form_file_button.setStyleSheet(
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
        button_layout.addWidget(form_file_button, alignment=Qt.AlignCenter)
        button_layout.setContentsMargins(45, 0, 65, 0)

    def edit_form_clicked(self):
        self.edit_form_button_clicked.emit(5, self.index, self.form_name)
        self.accept()


class DeleteMessageBox(QDialog):
    continue_button_clicked = pyqtSignal(int, str)

    def __init__(self, index, form_name, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 325)

        self.index = index
        self.form_name = form_name

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #EBEBEB;")

        title_label = QLabel("Delete Form")
        title_label.setStyleSheet(
            "font-size: 24px; font-family: Montserrat; font-weight: bold; color: #7C2F3E;"
        )
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        message_label = QLabel(
            f"You're currrently deleting {form_name}.\n\nDo you want to continue or discard."
        )
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 14px; font-family: Roboto; ")
        layout.addWidget(message_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        discard_button = QPushButton("Discard")
        discard_button.setFixedSize(100, 45)
        discard_button.clicked.connect(lambda: self.reject())
        discard_button.setStyleSheet(
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
        button_layout.addWidget(discard_button, alignment=Qt.AlignCenter)

        continue_button = QPushButton("Continue")
        continue_button.setFixedSize(100, 45)
        continue_button.clicked.connect(self.continue_clicked)
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

    def continue_clicked(self):
        self.continue_button_clicked.emit(self.index, self.form_name)
        self.close()


class DeleteButtonWidget(QWidget):
    # Define a new signal
    delete_button_clicked = pyqtSignal(int, str)

    def __init__(
        self, id_num, title_label, page_number_label, description_label, category
    ):
        super().__init__()
        self.index = id_num
        self.title_text = title_label
        self.page_number_text = page_number_label
        self.description_text = description_label
        self.category_text = category

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()  # Use QVBoxLayout for the main widget

        self.frame = QFrame(self)

        self.title_label = QLabel(self.title_text)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 19px;
            font-weight: bold;
            padding-top: 15px;
            padding-left: 15px;
            padding-right: 10px;
            color: #7C2F3E;
            """
        )

        self.category_label = QLabel(self.category_text)
        self.category_label.setStyleSheet(
            """
            font-family: Open Sans;
            font-size: 12px;
            padding-left: 15px;
            """
        )

        self.num_pages_layout = QHBoxLayout()

        self.bondpaper_img = QLabel()
        self.pixmap = QPixmap("./img/static/paper_img.png")
        self.bondpaper_img.setPixmap(self.pixmap)

        self.page_number_label = QLabel(self.page_number_text)

        self.num_pages_layout.addWidget(self.bondpaper_img)
        self.num_pages_layout.addWidget(self.page_number_label)

        self.num_pages_layout.setContentsMargins(15, 0, 240, 0)

        self.description_label = QLabel(self.description_text)
        self.description_label.setStyleSheet(
            """
            font-family: Open Sans;
            font-size: 12px;
            """
        )
        self.description_label.setWordWrap(True)
        self.description_label.setContentsMargins(15, 0, 10, 0)

        self.button = QPushButton("Delete")
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
                min-width: 120px;
                min-height: 120px;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        self.button.clicked.connect(self.emitButtonClickedSignal)

        form_content_layout = QVBoxLayout()  # Use QVBoxLayout for the form content

        form_content_layout.addWidget(self.title_label)
        form_content_layout.addWidget(self.category_label)
        form_content_layout.addLayout(self.num_pages_layout)
        form_content_layout.addWidget(self.description_label)

        layout.addLayout(form_content_layout)
        layout.addWidget(self.button, alignment=Qt.AlignRight)

        self.frame.setLayout(layout)

        self.setLayout(QVBoxLayout())  # Set layout to QVBoxLayout
        self.layout().addWidget(self.frame)  # Add the frame to the layout

    def emitButtonClickedSignal(self):
        # Emit the signal with necessary data
        self.delete_button_clicked.emit(self.index, self.title_text)


class EditButtonWidget(QWidget):
    # Define a new signal
    buttonClicked = pyqtSignal(int, str)

    def __init__(
        self, id_num, title_label, page_number_label, description_label, category
    ):
        super().__init__()
        self.index = id_num
        self.title_text = title_label
        self.page_number_text = page_number_label
        self.description_text = description_label
        self.category_text = category

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()  # Use QVBoxLayout for the main widget

        self.frame = QFrame(self)

        self.title_label = QLabel(self.title_text)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 19px;
            font-weight: bold;
            padding-top: 15px;
            padding-left: 15px;
            padding-right: 10px;
            color: #7C2F3E;
            """
        )

        self.category_label = QLabel(self.category_text)
        self.category_label.setStyleSheet(
            """
            font-family: Open Sans;
            font-size: 12px;
            padding-left: 15px;
            """
        )

        self.num_pages_layout = QHBoxLayout()

        self.bondpaper_img = QLabel()
        self.pixmap = QPixmap("./img/static/paper_img.png")
        self.bondpaper_img.setPixmap(self.pixmap)

        self.page_number_label = QLabel(self.page_number_text)

        self.num_pages_layout.addWidget(self.bondpaper_img)
        self.num_pages_layout.addWidget(self.page_number_label)

        self.num_pages_layout.setContentsMargins(15, 0, 240, 0)

        self.description_label = QLabel(self.description_text)
        self.description_label.setStyleSheet(
            """
            font-family: Open Sans;
            font-size: 12px;
            """
        )
        self.description_label.setWordWrap(True)
        self.description_label.setContentsMargins(15, 0, 10, 0)

        self.button = QPushButton("Edit")
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
                min-width: 120px;
                min-height: 120px;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        self.button.clicked.connect(self.emitButtonClickedSignal)

        form_content_layout = QVBoxLayout()  # Use QVBoxLayout for the form content

        form_content_layout.addWidget(self.title_label)
        form_content_layout.addWidget(self.category_label)
        form_content_layout.addLayout(self.num_pages_layout)
        form_content_layout.addWidget(self.description_label)

        layout.addLayout(form_content_layout)
        layout.addWidget(self.button, alignment=Qt.AlignRight)

        self.frame.setLayout(layout)

        self.setLayout(QVBoxLayout())  # Set layout to QVBoxLayout
        self.layout().addWidget(self.frame)  # Add the frame to the layout

    def emitButtonClickedSignal(self):
        # Emit the signal with necessary data
        self.buttonClicked.emit(self.index, self.title_text)


class FormWidget(QWidget):
    title_input_clicked = pyqtSignal()
    description_input_clicked = pyqtSignal()
    add_button_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT form_category FROM kiosk_forms")
        self.form_category = [category[0] for category in cursor.fetchall()]

        conn.close()

        # Main layout
        main_layout = QVBoxLayout(self)

        # Create a square QFrame to contain the form layout
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)  # Set fixed width to contain the layout
        frame.setStyleSheet(
            """
            background-color: #FFFFFF;
            border-radius: 15px;
            """
        )
        form_layout = QVBoxLayout(frame)  # Set the layout for the frame
        form_layout.addSpacerItem(
            QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(50)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 0)  # Adjust the shadow's offset as needed

        # Apply the effect to the rectangle
        frame.setGraphicsEffect(shadow_effect)

        # Title layout
        title_layout = QVBoxLayout()
        title_label = QLabel("Form Title:")
        title_label.setStyleSheet(
            """
            margin-top: 20px;
            font-family: Roboto;
            font-size: 16px;
            font-weight: bold;
            """
        )
        self.title_input = QLineEdit()
        self.title_input.setStyleSheet(
            """
            QLineEdit {
                font-family: Open Sans;
                border: 2px solid #b3b3b3;
                border-radius: 10px;
                padding-left: 10px;
                padding-right: 10px;
                padding-top: 15px;
                padding-bottom: 15px;
                font-size: 14px;
                background-color: #ffffff;
                color: #444444;
            }
            QLineEdit:focus {
                border: 2px solid #7C2F3E;
                background-color: #ffffff;
            }
            """
        )
        self.title_input.mousePressEvent = self.title_clicked
        self.title_input.setFixedWidth(300)
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)

        # Category layout
        category_layout = QVBoxLayout()
        category_label = QLabel("Form Category:")
        category_label.setStyleSheet(
            """
            margin-top: 20px;
            font-family: Roboto;
            font-size: 16px;
            font-weight: bold;
            """
        )
        self.category_input = QComboBox()
        self.category_input.setStyleSheet(
            """
            QComboBox {
                border: 2px solid #B3B3B3;
                border-radius: 0px;
                padding-left: 10px;
                padding-top: 15px;
                padding-bottom: 15px;
                font-family: Roboto;
                font-size: 14px;
                color: #444444;
            }
            QComboBox:focus {
                border: 2px solid #7C2F3E;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;  /* Adjusted position */
                
                width: 20px;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #5c9ded;
                font-size: 14px;
            }
            """
        )
        self.category_input.addItems(self.form_category)
        self.category_input.setFixedWidth(300)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_input)

        # Page number layout
        page_number_layout = QVBoxLayout()
        pages_label = QLabel("Number of Pages:")
        pages_label.setStyleSheet(
            """
            margin-top: 20px;
            font-family: Roboto;
            font-size: 16px;
            font-weight: bold;
            """
        )
        self.page_input = QSpinBox()
        self.page_input.setStyleSheet(
            """
            QSpinBox {
                border: 2px solid #B3B3B3;
                padding-left: 10px;
                padding-top: 15px;
                padding-bottom: 15px;
                font-size: 14px;
                color: #444444;
                border-radius: 0px;
            }
            QSpinBox:focus {
                border: 2px solid #7C2F3E;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 25px;
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 25px;
            }
            """
        )
        self.page_input.setMinimum(1)
        self.page_input.setMaximum(10)
        self.page_input.setFixedWidth(300)
        page_number_layout.addWidget(pages_label)
        page_number_layout.addWidget(self.page_input)

        # Upper form layout
        upper_form_layout = QHBoxLayout()
        upper_form_layout.addLayout(title_layout)
        upper_form_layout.addLayout(category_layout)
        upper_form_layout.addLayout(page_number_layout)

        upper_form_layout.setContentsMargins(15, 0, 15, 0)
        form_layout.addLayout(upper_form_layout)
        form_layout.addSpacerItem(
            QSpacerItem(20, 35, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Form description layout
        form_description_layout = QVBoxLayout()
        description_label = QLabel("Form Description:")
        description_label.setStyleSheet(
            """
            margin-top: 20px;
            font-family: Roboto;
            font-size: 16px;
            font-weight: bold;
            """
        )
        self.description_input = QTextEdit()
        self.description_input.setStyleSheet(
            """
            QTextEdit {
                border: 2px solid #b3b3b3;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                color: #444444;
                background-color: #ffffff;
            }
            QTextEdit:focus {
                border: 2px solid #7C2F3E;
            }
            """
        )
        self.description_input.mousePressEvent = self.description_clicked
        form_description_layout.addWidget(description_label)
        form_description_layout.addWidget(self.description_input)
        form_description_layout.setContentsMargins(95, 0, 95, 0)

        form_layout.addLayout(form_description_layout)
        form_layout.addSpacerItem(
            QSpacerItem(20, 35, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Lower form layout
        lower_form_layout = QHBoxLayout()

        self.upload_form_widget = UploadFormWidget()
        self.upload_form_widget.setFixedSize(300, 300)
        self.upload_form_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.upload_process_widget = UploadProcessWidget()
        self.upload_process_widget.setFixedSize(300, 300)
        self.upload_process_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        lower_form_layout.addWidget(self.upload_form_widget)
        lower_form_layout.addSpacerItem(
            QSpacerItem(50, 25, QSizePolicy.Fixed, QSizePolicy.Fixed)
        )
        lower_form_layout.addWidget(self.upload_process_widget)
        lower_form_layout.setAlignment(Qt.AlignLeft)
        lower_form_layout.setContentsMargins(90, 0, 0, 0)

        form_layout.addLayout(lower_form_layout)
        form_layout.addSpacerItem(
            QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        add_clear_button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.setStyleSheet(
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
        self.add_button.setFixedSize(170, 65)
        self.add_button.clicked.connect(self.add_file)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet(
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
        self.clear_button.setFixedSize(170, 65)
        self.clear_button.clicked.connect(self.clear)

        add_clear_button_layout.addWidget(self.clear_button)
        add_clear_button_layout.addItem(
            QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )
        add_clear_button_layout.addWidget(self.add_button)

        self.add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.clear_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        add_clear_button_layout.setAlignment(Qt.AlignRight)
        add_clear_button_layout.setContentsMargins(0, 0, 90, 0)

        form_layout.addLayout(add_clear_button_layout)

        form_layout.addSpacerItem(
            QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Add the frame to the main layout
        main_layout.addWidget(frame)
        main_layout.addStretch(1)  # Adjust as needed
        self.setLayout(main_layout)

    def title_clicked(self, event):
        self.title_input_clicked.emit()

    def description_clicked(self, event):
        self.description_input_clicked.emit()

    def clear(self):
        self.title_input.clear()
        self.category_input.setCurrentIndex(0)
        self.page_input.setValue(1)
        self.description_input.clear()

        self.upload_form_widget.clearSelectedFile()
        self.upload_process_widget.clearSelectedFile()

    def check_inputs(self):
        return not any(
            [
                self.title_input.text().strip() == "",
                self.description_input.toPlainText().strip() == "",
            ]
        )

    def add_sql_data(self, form_title, num_page, form_description, form_category):
        try:
            conn = sqlite3.connect("kiosk.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO kiosk_forms (form_name, number_of_pages, form_description, form_category) VALUES (?,?,?,?)",
                (form_title, num_page, form_description, form_category),
            )

            # Commit the transaction to save changes
            conn.commit()

            print("Data inserted successfully.")

        except sqlite3.Error as e:
            print("SQLite error:", e)

        finally:
            # Close the connection
            conn.close()

    def add_file(self):
        if (
            self.upload_form_widget.check_input()
            and self.check_inputs()
            and self.upload_process_widget.check_input()
        ):
            form_title = self.title_input.text().title().strip()
            num_page = self.page_input.value()
            form_description = self.description_input.toPlainText().strip()
            form_category = self.category_input.currentText()

            self.add_sql_data(
                str(form_title),
                int(num_page),
                str(form_description),
                str(form_category),
            )

            form_file_path = self.upload_form_widget.get_file()
            upload_form_file(form_file_path, form_title)

            process_file_path = self.upload_process_widget.get_file()
            upload_process_file(process_file_path, form_title)

            self.add_button_clicked.emit()

            message_box = CustomMessageBox(
                "Success",
                f"{form_title} has been successfully added.",
                parent=self,
            )
            message_box.exec_()

            self.clear()

        else:
            # Display dialog box indicating success
            message_box = CustomMessageBox(
                "Error",
                "Please fill in all required fields before proceeding.",
                parent=self,
            )
            message_box.exec_()


class EditFormWidget(QWidget):
    title_input_clicked = pyqtSignal()
    description_input_clicked = pyqtSignal()
    edit_form_success = pyqtSignal()

    def __init__(self, id_num, form_name):
        super().__init__()
        self.initUI(id_num, form_name)

    def initUI(self, id_num, form_name):
        self.id_num = id_num
        self.form_title = form_name

        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT form_category FROM kiosk_forms")
        self.form_category = [category[0] for category in cursor.fetchall()]

        conn.close()

        # Main layout
        main_layout = QVBoxLayout(self)

        # Create a square QFrame to contain the form layout
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)  # Set fixed width to contain the layout
        frame.setStyleSheet(
            """
            background-color: #FFFFFF;
            border-radius: 15px;
            """
        )
        form_layout = QVBoxLayout(frame)  # Set the layout for the frame
        form_layout.addSpacerItem(
            QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(50)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 0)  # Adjust the shadow's offset as needed

        # Apply the effect to the rectangle
        frame.setGraphicsEffect(shadow_effect)

        # Title layout
        title_layout = QVBoxLayout()
        title_label = QLabel("Form Title:")
        title_label.setStyleSheet(
            """
            margin-top: 20px;
            font-family: Roboto;
            font-size: 16px;
            font-weight: bold;
            """
        )
        self.title_input = QLineEdit()
        self.title_input.setStyleSheet(
            """
            QLineEdit {
                font-family: Open Sans;
                border: 2px solid #b3b3b3;
                border-radius: 10px;
                padding-left: 10px;
                padding-right: 10px;
                padding-top: 15px;
                padding-bottom: 15px;
                font-size: 14px;
                background-color: #ffffff;
                color: #444444;
            }
            QLineEdit:focus {
                border: 2px solid #7C2F3E;
                background-color: #ffffff;
            }
            """
        )
        self.title_input.mousePressEvent = self.title_clicked
        self.title_input.setFixedWidth(300)
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)

        # Category layout
        category_layout = QVBoxLayout()
        category_label = QLabel("Form Category:")
        category_label.setStyleSheet(
            """
            margin-top: 20px;
            font-family: Roboto;
            font-size: 16px;
            font-weight: bold;
            """
        )
        self.category_input = QComboBox()
        self.category_input.setStyleSheet(
            """
            QComboBox {
                border: 2px solid #B3B3B3;
                border-radius: 0px;
                padding-left: 10px;
                padding-top: 15px;
                padding-bottom: 15px;
                font-family: Roboto;
                font-size: 14px;
                color: #444444;
            }
            QComboBox:focus {
                border: 2px solid #7C2F3E;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;  /* Adjusted position */
                
                width: 20px;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #5c9ded;
                font-size: 14px;
            }
            """
        )
        self.category_input.addItems(self.form_category)
        self.category_input.setFixedWidth(300)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_input)

        # Page number layout
        page_number_layout = QVBoxLayout()
        pages_label = QLabel("Number of Pages:")
        pages_label.setStyleSheet(
            """
            margin-top: 20px;
            font-family: Roboto;
            font-size: 16px;
            font-weight: bold;
            """
        )
        self.page_input = QSpinBox()
        self.page_input.setStyleSheet(
            """
            QSpinBox {
                border: 2px solid #B3B3B3;
                padding-left: 10px;
                padding-top: 15px;
                padding-bottom: 15px;
                font-size: 14px;
                color: #444444;
                border-radius: 0px;
            }
            QSpinBox:focus {
                border: 2px solid #7C2F3E;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 25px;
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 25px;
            }
            """
        )
        self.page_input.setMinimum(1)
        self.page_input.setMaximum(10)
        self.page_input.setFixedWidth(300)
        page_number_layout.addWidget(pages_label)
        page_number_layout.addWidget(self.page_input)

        # Upper form layout
        upper_form_layout = QHBoxLayout()
        upper_form_layout.addLayout(title_layout)
        upper_form_layout.addLayout(category_layout)
        upper_form_layout.addLayout(page_number_layout)

        upper_form_layout.setContentsMargins(15, 0, 15, 0)
        form_layout.addLayout(upper_form_layout)
        form_layout.addSpacerItem(
            QSpacerItem(20, 35, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Form description layout
        form_description_layout = QVBoxLayout()
        description_label = QLabel("Form Description:")
        description_label.setStyleSheet(
            """
            margin-top: 20px;
            font-family: Roboto;
            font-size: 16px;
            font-weight: bold;
            """
        )
        self.description_input = QTextEdit()
        self.description_input.setStyleSheet(
            """
            QTextEdit {
                border: 2px solid #b3b3b3;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                color: #444444;
                background-color: #ffffff;
            }
            QTextEdit:focus {
                border: 2px solid #7C2F3E;
            }
            """
        )
        self.description_input.mousePressEvent = self.description_clicked
        form_description_layout.addWidget(description_label)
        form_description_layout.addWidget(self.description_input)
        form_description_layout.setContentsMargins(95, 0, 95, 0)

        form_layout.addLayout(form_description_layout)
        form_layout.addSpacerItem(
            QSpacerItem(20, 35, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Lower form layout
        lower_form_layout = QHBoxLayout()

        self.upload_form_widget = UploadFormWidget()
        self.upload_form_widget.setFixedSize(300, 300)
        self.upload_form_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.upload_process_widget = UploadProcessWidget()
        self.upload_process_widget.setFixedSize(300, 300)
        self.upload_process_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        lower_form_layout.addWidget(self.upload_form_widget)
        lower_form_layout.addSpacerItem(
            QSpacerItem(50, 25, QSizePolicy.Fixed, QSizePolicy.Fixed)
        )
        lower_form_layout.addWidget(self.upload_process_widget)
        lower_form_layout.setAlignment(Qt.AlignLeft)
        lower_form_layout.setContentsMargins(90, 0, 0, 0)

        form_layout.addLayout(lower_form_layout)
        form_layout.addSpacerItem(
            QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        add_clear_button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.setStyleSheet(
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
        self.add_button.setFixedSize(170, 65)
        self.add_button.clicked.connect(self.add_file)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet(
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
        self.clear_button.setFixedSize(170, 65)
        self.clear_button.clicked.connect(self.clear)

        add_clear_button_layout.addWidget(self.clear_button)
        add_clear_button_layout.addItem(
            QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )
        add_clear_button_layout.addWidget(self.add_button)

        self.add_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.clear_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        add_clear_button_layout.setAlignment(Qt.AlignRight)
        add_clear_button_layout.setContentsMargins(0, 0, 90, 0)

        form_layout.addLayout(add_clear_button_layout)

        form_layout.addSpacerItem(
            QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Add the frame to the main layout
        main_layout.addWidget(frame)
        main_layout.addStretch(1)  # Adjust as needed
        self.setLayout(main_layout)

    def title_clicked(self, event):
        self.title_input_clicked.emit()

    def description_clicked(self, event):
        self.description_input_clicked.emit()

    def clear(self):
        self.title_input.clear()
        self.category_input.setCurrentIndex(0)
        self.page_input.setValue(1)
        self.description_input.clear()

        self.upload_form_widget.clearSelectedFile()
        self.upload_process_widget.clearSelectedFile()

    def check_inputs(self):
        return not any(
            [
                self.title_input.text().strip() == "",
                self.description_input.toPlainText().strip() == "",
            ]
        )

    def add_sql_data(self, form_title, num_page, form_description, form_category):
        try:
            conn = sqlite3.connect("kiosk.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE kiosk_forms 
                SET 
                    form_name = ?, 
                    number_of_pages = ?, 
                    form_description = ?, 
                    form_category = ?
                WHERE 
                    id = ?
                """,
                (form_title, num_page, form_description, form_category, self.id_num),
            )

            # Commit the transaction to save changes
            conn.commit()

            print("Data updated successfully.")

        except sqlite3.Error as e:
            print("SQLite error:", e)

        finally:
            # Close the connection
            conn.close()

    def add_file(self):
        if (
            self.upload_form_widget.check_input()
            and self.check_inputs()
            and self.upload_process_widget.check_input()
        ):
            form_title = self.title_input.text().title().strip()
            num_page = self.page_input.value()
            form_description = self.description_input.toPlainText().strip()
            form_category = self.category_input.currentText()

            self.add_sql_data(
                str(form_title),
                int(num_page),
                str(form_description),
                str(form_category),
            )

            form_file_path = self.upload_form_widget.get_file()
            upload_form_file(form_file_path, self.form_title)

            process_file_path = self.upload_process_widget.get_file()
            upload_process_file(process_file_path, self.form_title)

            self.edit_form_file_success.emit()

            message_box = CustomMessageBox(
                "Success",
                f"{form_title} has been successfully added.",
                parent=self,
            )
            message_box.exec_()

            self.clear()

        else:
            # Display dialog box indicating success
            message_box = CustomMessageBox(
                "Error",
                "Please fill in all required fields before proceeding.",
                parent=self,
            )
            message_box.exec_()


class UploadFormWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a frame to contain the widget
        self.frame = QFrame(self)
        self.frame.setStyleSheet(
            """
            QFrame {
                border: 3px solid #b3b3b3;
                border-radius: 25px;
                background-color: #FFFFFF;
            }
            """
        )

        layout = QVBoxLayout(self.frame)

        self.selected_file_path = None

        # Create and add the first label
        form_upload_label = QLabel("Form Upload")
        form_upload_label.setStyleSheet(
            """
            border: none;
            font-family: Roboto;
            font-size: 18px;
            font-weight: bold;
            margin-top: 15px;
            """
        )
        layout.addWidget(form_upload_label, alignment=Qt.AlignCenter)

        self.image_label = QLabel()
        pixmap = QPixmap("./img/static/upload_img.png")
        scaled_pixmap = pixmap.scaled(
            120, 120, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("border: none")
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # Create and add the button
        self.browse_button = QPushButton("Browse")
        self.browse_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                color: #FAEBD7; 
                border: none;
                border-radius: 15px;
                color: white;
                font-family: Montserrat;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        self.browse_button.setFixedSize(170, 35)
        self.browse_button.clicked.connect(self.open_file_explorer)
        layout.addWidget(self.browse_button, alignment=Qt.AlignCenter)

        # Create and add the second label
        self.file_label = QLabel()
        self.file_label.setStyleSheet(
            """
            border: none;
            font-family: Open Sans;
            font-size: 14px;
            background-color: transparent;
            """
        )
        layout.addWidget(self.file_label, alignment=Qt.AlignCenter)

        # Set layout margins and spacing
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Set the frame's layout
        self.frame.setLayout(layout)

        # Set the layout of UploadFormWidget
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(
            self.frame
        )  # Add the frame to UploadFormWidget's layout

    def open_file_explorer(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # Use native dialog on macOS
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Document (*.pdf)", options=options
        )
        if file_path:
            file_name = os.path.basename(file_path)
            print("Selected file:", file_name)
            self.display_file_preview(file_name)
            self.selected_file_path = file_path

    def display_file_preview(self, file_name):
        self.file_label.setText(f"Selected File: {file_name}")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet(
            """
            border: none;
            font-family: Open Sans;
            font-size: 14px;
            color: #535353;
            padding-left: 10px;
            padding-right: 10px;
            background-color: transparent;
            """
        )
        self.frame.setStyleSheet(
            """
            QFrame {
                border: 3px solid #7C2F3E;
                border-radius: 25px;
                background-color: #FFFFFF;
            }
            """
        )

    def clearSelectedFile(self):
        self.selected_file_path = None
        self.file_label.clear()

    def get_file(self):
        return self.selected_file_path

    def check_input(self):
        return self.selected_file_path is not None


class UploadProcessWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a frame to contain the widget
        self.frame = QFrame(self)
        self.frame.setStyleSheet(
            """
            QFrame {
                border: 3px solid #b3b3b3;
                border-radius: 25px;
                background-color: #FFFFFF;
            }
            """
        )

        layout = QVBoxLayout(self.frame)

        # Create and add the first label
        form_upload_label = QLabel("Process Upload")
        form_upload_label.setStyleSheet(
            """
            border: none;
            font-family: Roboto;
            font-size: 18px;
            font-weight: bold;
            margin-top: 15px;
            """
        )
        layout.addWidget(form_upload_label, alignment=Qt.AlignCenter)

        self.image_label = QLabel()
        pixmap = QPixmap("./img/static/upload_img.png")
        scaled_pixmap = pixmap.scaled(
            120, 120, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("border: none")
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        # Create and add the button
        self.browse_button = QPushButton("Browse")
        self.browse_button.setStyleSheet(
            """
            QPushButton {
                background-color: #7C2F3E;
                color: #FAEBD7; 
                border: none;
                border-radius: 15px;
                color: white;
                font-family: Montserrat;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: #D8973C;
            }
            """
        )
        self.browse_button.setFixedSize(170, 35)
        self.browse_button.clicked.connect(self.open_file_explorer)
        layout.addWidget(self.browse_button, alignment=Qt.AlignCenter)

        # Create and add the second label
        self.file_label = QLabel()
        self.file_label.setStyleSheet(
            """
            border: none;
            font-family: Open Sans;
            font-size: 14px;
            background-color: transparent;
            """
        )
        layout.addWidget(self.file_label, alignment=Qt.AlignCenter)

        # Set layout margins and spacing
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Set the frame's layout
        self.frame.setLayout(layout)

        # Set the layout of UploadFormWidget
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(
            self.frame
        )  # Add the frame to UploadFormWidget's layout

    def open_file_explorer(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # Use native dialog on macOS
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Images (*.png *.jpg *.jpeg *.bmp)", options=options
        )
        if file_path:
            file_name = os.path.basename(file_path)
            print("Selected file:", file_name)
            self.display_file_preview(file_name)
            self.selected_file_path = file_path

    def display_file_preview(self, file_name):
        self.file_label.setText(f"Selected File: {file_name}")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet(
            """
            border: none;
            font-family: Open Sans;
            font-size: 14px;
            color: #535353;
            padding-left: 10px;
            padding-right: 10px;
            background-color: transparent;
            """
        )
        self.frame.setStyleSheet(
            """
            QFrame {
                border: 3px solid #7C2F3E;
                border-radius: 25px;
                background-color: #FFFFFF;
            }
            """
        )

    def clearSelectedFile(self):
        self.selected_file_path = None
        self.file_label.clear()

    def get_file(self):
        return self.selected_file_path

    def check_input(self):
        return self.selected_file_path is not None


class CustomButton(QPushButton):
    def __init__(self, text, image_path, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()

        self.label = QLabel(text)
        self.label.setStyleSheet(
            """
            font-family: Roboto, sans-serif; 
            font-size: 14px;
            font-weight: bold;
            color: #19323C;
            padding-right: 3px;
            """
        )

        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            35, 35, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label = QLabel()
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("margin-left: 25px;")

        layout.addWidget(self.image_label)
        layout.addWidget(self.label, alignment=Qt.AlignLeft)

        self.setFocusPolicy(Qt.NoFocus)
        self.setLayout(layout)


class TotalAmountDropButton(QPushButton):
    weekly_selected = pyqtSignal(float)
    monthly_selected = pyqtSignal(float)
    yearly_selected = pyqtSignal(float)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QMenu
        self.menu = QMenu(self)

        # Create actions for the menu
        self.action1 = QAction("Weekly", self)
        self.action2 = QAction("Monthly", self)
        self.action3 = QAction("Yearly", self)

        # Connect actions to their respective slots
        self.action1.triggered.connect(self.sort_weekly)
        self.action2.triggered.connect(self.sort_monthly)
        self.action3.triggered.connect(self.sort_yearly)

        # Add actions to the menu
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)

        self.setMenu(self.menu)

        # Use a stylesheet to make the menu appear below the button
        self.menu.setStyleSheet(
            """
            QMenu {
                left: 0;
            }
        """
        )

        # Set initial state to "Weekly"
        self.setText("Weekly")
        self.sort_weekly()

    def sort_weekly(self):
        self.setText("Weekly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        # Get the current week's start and end dates
        current_date = datetime.datetime.now()
        start_of_week = current_date - datetime.timedelta(days=current_date.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        # Execute the SQL query to sum the total amount based on the current week
        cursor.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0) AS total_amount
            FROM kiosk_print_results
            WHERE date(date_printed) BETWEEN ? AND ? AND result = 'Success'
            """,
            (start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")),
        )

        # Fetch the result
        self.total_amount = cursor.fetchone()[0]

        # Close the cursor and database connection
        cursor.close()
        conn.close()

        self.weekly_selected.emit(self.total_amount)

    def get_weekly_amount(self):
        return float(self.total_amount)

    def sort_monthly(self):
        self.setText("Monthly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        # Get the current month and year
        current_month = datetime.datetime.now().strftime("%Y-%m")

        # Execute the SQL query to sum the total amount based on the current month
        cursor.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0) AS total_amount
            FROM kiosk_print_results
            WHERE strftime('%Y-%m', date_printed) = ? AND result = 'Success'
            """,
            (current_month,),
        )

        # Fetch the result
        total_amount = cursor.fetchone()[0]

        # Close the cursor and database connection
        cursor.close()
        conn.close()

        self.monthly_selected.emit(total_amount)

    def sort_yearly(self):
        self.setText("Yearly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        # Get the current year
        current_year = datetime.datetime.now().strftime("%Y")

        # Execute the SQL query to sum the total amount based on the current year
        cursor.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0) AS total_amount
            FROM kiosk_print_results
            WHERE strftime('%Y', date_printed) = ? AND result = 'Success'
            """,
            (current_year,),
        )

        # Fetch the result
        total_amount = cursor.fetchone()[0]

        # Close the cursor and database connection
        cursor.close()
        conn.close()

        self.yearly_selected.emit(total_amount)


class TotalFormDropButton(QPushButton):
    weekly_selected = pyqtSignal(str)
    monthly_selected = pyqtSignal(str)
    yearly_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QMenu
        self.menu = QMenu()

        # Create actions for the menu
        self.action1 = QAction("Weekly", self)
        self.action2 = QAction("Monthly", self)
        self.action3 = QAction("Yearly", self)

        # Connect actions to their respective slots
        self.action1.triggered.connect(self.sort_weekly)
        self.action2.triggered.connect(self.sort_monthly)
        self.action3.triggered.connect(self.sort_yearly)

        # Add actions to the menu
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)

        self.setMenu(self.menu)

        # Set initial state to "Weekly"
        self.setText("Weekly")
        self.sort_weekly()

    def sort_weekly(self):
        self.setText("Weekly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        # Get the start and end dates for the current week
        today = datetime.datetime.now()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        cursor.execute(
            """
            SELECT COALESCE(
                    (SELECT form_name
                        FROM kiosk_print_results
                        WHERE strftime('%Y-%m-%d', date_printed) BETWEEN ? AND ? 
                            AND result = 'Success'
                        GROUP BY form_name
                        ORDER BY SUM(number_of_copies) DESC
                        LIMIT 1
                    ), 'None'
                )
        """,
            (start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")),
        )

        self.total_form = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.weekly_selected.emit(self.total_form)

    def get_weekly_amount(self):
        return self.total_form

    def sort_monthly(self):
        self.setText("Monthly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        current_month = datetime.datetime.now().strftime("%Y-%m")

        cursor.execute(
            """
            SELECT COALESCE(
                    (SELECT form_name
                        FROM kiosk_print_results
                        WHERE strftime('%Y-%m', date_printed) = ? 
                            AND result = 'Success'
                        GROUP BY form_name
                        ORDER BY SUM(number_of_copies) DESC
                        LIMIT 1
                    ), 'None'
                )
        """,
            (current_month,),
        )

        total_form = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.monthly_selected.emit(total_form)

    def sort_yearly(self):
        self.setText("Yearly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        current_year = datetime.datetime.now().strftime("%Y")

        cursor.execute(
            """
            SELECT COALESCE(
                    (SELECT form_name
                        FROM kiosk_print_results
                        WHERE strftime('%Y', date_printed) = ? 
                            AND result = 'Success'
                        GROUP BY form_name
                        ORDER BY SUM(number_of_copies) DESC
                        LIMIT 1
                    ), 'None'
                )
        """,
            (current_year,),
        )

        total_form = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.yearly_selected.emit(total_form)


class TotalFailedDropButton(QPushButton):
    weekly_selected = pyqtSignal(int)
    monthly_selected = pyqtSignal(int)
    yearly_selected = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QMenu
        self.menu = QMenu(self)

        # Create actions for the menu
        self.action1 = QAction("Weekly", self)
        self.action2 = QAction("Monthly", self)
        self.action3 = QAction("Yearly", self)

        # Connect actions to their respective slots
        self.action1.triggered.connect(self.sort_weekly)
        self.action2.triggered.connect(self.sort_monthly)
        self.action3.triggered.connect(self.sort_yearly)

        # Add actions to the menu
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)

        self.setMenu(self.menu)

        # Use a stylesheet to make the menu appear below the button
        self.menu.setStyleSheet(
            """
            QMenu {
                left: 0;
            }
        """
        )

        # Set initial state to "Weekly"
        self.setText("Weekly")
        self.sort_weekly()

    def sort_weekly(self):
        self.setText("Weekly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        # Get the start and end dates for the current week
        today = datetime.datetime.now()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        cursor.execute(
            """
            SELECT COUNT(*) AS total_failed_count
            FROM kiosk_print_results
            WHERE result = 'Failed'
            AND date(date_printed) BETWEEN ? AND ?
        """,
            (start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")),
        )

        self.total_error = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.weekly_selected.emit(self.total_error)

    def get_weekly_amount(self):
        return self.total_error

    def sort_monthly(self):
        self.setText("Monthly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        current_month = datetime.datetime.now().strftime("%Y-%m")

        cursor.execute(
            """
            SELECT COUNT(*) AS total_failed_count
            FROM kiosk_print_results
            WHERE result = 'Failed'
            AND strftime('%Y-%m', date_printed) = ?
        """,
            (current_month,),
        )

        total_error = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.monthly_selected.emit(total_error)

    def sort_yearly(self):
        self.setText("Yearly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        current_year = datetime.datetime.now().strftime("%Y")

        cursor.execute(
            """
            SELECT COUNT(*) AS total_failed_count
            FROM kiosk_print_results
            WHERE result = 'Failed'
            AND strftime('%Y', date_printed) = ?
        """,
            (current_year,),
        )

        total_error = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.yearly_selected.emit(total_error)


class TotalSuccessDropButton(QPushButton):
    weekly_selected = pyqtSignal(int)
    monthly_selected = pyqtSignal(int)
    yearly_selected = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QMenu
        self.menu = QMenu(self)

        # Create actions for the menu
        self.action1 = QAction("Weekly", self)
        self.action2 = QAction("Monthly", self)
        self.action3 = QAction("Yearly", self)

        # Connect actions to their respective slots
        self.action1.triggered.connect(self.sort_weekly)
        self.action2.triggered.connect(self.sort_monthly)
        self.action3.triggered.connect(self.sort_yearly)

        # Add actions to the menu
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)

        self.setMenu(self.menu)

        # Use a stylesheet to make the menu appear below the button
        self.menu.setStyleSheet(
            """
            QMenu {
                left: 0;
            }
        """
        )

        # Set initial state to "Weekly"
        self.setText("Weekly")
        self.sort_weekly()

    def sort_weekly(self):
        self.setText("Weekly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        # Get the start and end dates for the current week
        today = datetime.datetime.now()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        cursor.execute(
            """
            SELECT COUNT(*) AS total_failed_count
            FROM kiosk_print_results
            WHERE result = 'Success'
            AND date(date_printed) BETWEEN ? AND ?
        """,
            (start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")),
        )

        self.total_success = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.weekly_selected.emit(self.total_success)

    def get_weekly_amount(self):
        return self.total_success

    def sort_monthly(self):
        self.setText("Monthly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        current_month = datetime.datetime.now().strftime("%Y-%m")

        cursor.execute(
            """
            SELECT COUNT(*) AS total_failed_count
            FROM kiosk_print_results
            WHERE result = 'Success'
            AND strftime('%Y-%m', date_printed) = ?
        """,
            (current_month,),
        )

        total_success = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.monthly_selected.emit(total_success)

    def sort_yearly(self):
        self.setText("Yearly")

        # Connect to the database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        current_year = datetime.datetime.now().strftime("%Y")

        cursor.execute(
            """
            SELECT COUNT(*) AS total_failed_count
            FROM kiosk_print_results
            WHERE result = 'Success'
            AND strftime('%Y', date_printed) = ?
        """,
            (current_year,),
        )

        total_success = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.yearly_selected.emit(total_success)


class TotalAmountWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create a QFrame
        frame = QFrame(self)
        frame.setAutoFillBackground(True)  # Enable background color

        # Set background color (for example, light gray)
        p = frame.palette()
        p.setColor(frame.backgroundRole(), QColor(255, 255, 255))
        frame.setPalette(p)

        # Create a layout for the frame
        main_layout = QVBoxLayout(frame)

        # Create labels
        top_layout = QHBoxLayout()
        image_label = QLabel()

        button = TotalAmountDropButton()
        button.setFixedSize(120, 40)

        button.weekly_selected.connect(self.change_total_label)
        button.monthly_selected.connect(self.change_total_label)
        button.yearly_selected.connect(self.change_total_label)

        weekly_total = button.get_weekly_amount()

        top_layout.addWidget(image_label)
        top_layout.addWidget(button)

        text_label = QLabel("Total Amount Collected:")
        text_label.setStyleSheet(
            """
            font-family: Roboto;
            font-size: 10px;
            margin-left: 17px;
            color: #ADADAD;
            border: none;
            padding-bottom: 10px;
            """
        )

        self.total_label = QLabel(f"₱ {weekly_total}")
        self.total_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-weight: bold;
            font-size: 13px;
            margin-left: 15px;
            padding-top: 7px;
            border: none;
            """
        )

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(text_label)

        frame.setLayout(main_layout)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(frame)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def change_total_label(self, total_amount):
        self.total_label.setText(f"₱ {total_amount}")


class TotalFormWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create a QFrame
        frame = QFrame(self)
        frame.setAutoFillBackground(True)  # Enable background color

        # Set background color (for example, light gray)
        p = frame.palette()
        p.setColor(frame.backgroundRole(), QColor(255, 255, 255))
        frame.setPalette(p)

        # Create a layout for the frame
        main_layout = QVBoxLayout(frame)

        # Create labels
        top_layout = QHBoxLayout()
        image_label = QLabel()
        image_label.setStyleSheet("border: none;")

        button = TotalFormDropButton()
        button.setFixedSize(120, 40)

        button.weekly_selected.connect(self.change_total_label)
        button.monthly_selected.connect(self.change_total_label)
        button.yearly_selected.connect(self.change_total_label)

        weekly_total = button.get_weekly_amount()

        top_layout.addWidget(image_label)
        top_layout.addWidget(button)

        text_label = QLabel("Most Printed Form:")
        text_label.setStyleSheet(
            """
            font-family: Roboto;
            font-size: 10px;
            margin-left: 17px;
            color: #ADADAD;
            border: none;
            padding-bottom: 10px;
            """
        )

        self.total_label = QLabel(f"{weekly_total}")
        self.total_label.setWordWrap(True)
        self.total_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-weight: bold;
            font-size: 13px;
            margin-left: 15px;
            padding-top: 7px;
            border: none;
            """
        )

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(text_label)

        frame.setLayout(main_layout)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(frame)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def change_total_label(self, total_amount):
        self.total_label.setText(f"{total_amount}")


class TotalSuccessWidget(QWidget):
    def __init__(self):
        super().__init__()

        frame = QFrame(self)
        frame.setAutoFillBackground(True)  # Enable background color

        # Set background color (for example, light gray)
        p = frame.palette()
        p.setColor(frame.backgroundRole(), QColor(255, 255, 255))
        frame.setPalette(p)

        main_layout = QVBoxLayout(frame)

        top_layout = QHBoxLayout()
        image_label = QLabel()

        button = TotalSuccessDropButton()
        button.setFixedSize(120, 40)

        button.weekly_selected.connect(self.change_total_label)
        button.monthly_selected.connect(self.change_total_label)
        button.yearly_selected.connect(self.change_total_label)

        weekly_total = button.get_weekly_amount()

        top_layout.addWidget(image_label)
        top_layout.addWidget(button)

        text_label = QLabel("Forms Printed Successfully:")
        text_label.setStyleSheet(
            """
            font-family: Roboto;
            font-size: 10px;
            margin-left: 17px;
            color: #ADADAD;
            border: none;
            padding-bottom: 10px;
            """
        )

        self.total_label = QLabel(f"{weekly_total}")
        self.total_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-weight: bold;
            font-size: 13px;
            margin-left: 15px;
            padding-top: 7px;
            border: none;
            """
        )

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(text_label)

        frame.setLayout(main_layout)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(frame)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def change_total_label(self, total_amount):
        self.total_label.setText(f"{total_amount}")


class TotalFailedWidget(QWidget):
    def __init__(self):
        super().__init__()

        frame = QFrame(self)
        frame.setAutoFillBackground(True)  # Enable background color

        # Set background color (for example, light gray)
        p = frame.palette()
        p.setColor(frame.backgroundRole(), QColor(255, 255, 255))
        frame.setPalette(p)

        main_layout = QVBoxLayout(frame)

        top_layout = QHBoxLayout()
        image_label = QLabel()

        button = TotalFailedDropButton()
        button.setFixedSize(120, 40)

        button.weekly_selected.connect(self.change_total_label)
        button.monthly_selected.connect(self.change_total_label)
        button.yearly_selected.connect(self.change_total_label)

        weekly_total = button.get_weekly_amount()

        top_layout.addWidget(image_label)
        top_layout.addWidget(button)

        text_label = QLabel("Forms Printed Uncessfully:")
        text_label.setStyleSheet(
            """
            font-family: Roboto;
            font-size: 10px;
            margin-left: 17px;
            color: #ADADAD;
            border: none;
            padding-bottom: 10px;
            """
        )

        self.total_label = QLabel(f"{weekly_total}")
        self.total_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-weight: bold;
            font-size: 13px;
            margin-left: 15px;
            padding-top: 7px;
            border: none;
            """
        )

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(text_label)

        frame.setLayout(main_layout)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(frame)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def change_total_label(self, total_amount):
        self.total_label.setText(f"{total_amount}")


class AdminWindowWidget(QWidget):
    home_screen_backbt_clicked = pyqtSignal()
    bondpaper_quantity_updated = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)

        # Define instance variables for temporary values
        self.id_num = 0
        self.form_name = " "

        # Create and position the virtual keyboard
        self.virtual_keyboard = AlphaNeumericVirtualKeyboard("", parent=self)

        # Set window flags to make the keyboard stay on top
        self.virtual_keyboard.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.virtual_keyboard.hide()

        # add tabs
        self.tab1 = self.ui1()
        self.tab2 = self.ui2()
        self.tab3 = self.ui3()
        self.tab4 = self.ui4()
        self.tab5 = self.ui5()
        self.tab6 = self.ui6()

        self.setup_ui()

        self.btn_1.clicked.connect(self.button1)
        self.btn_2.clicked.connect(self.button2)
        self.btn_3.clicked.connect(self.button3)
        self.btn_4.clicked.connect(self.button4)
        self.btn_5.clicked.connect(self.button5)
        self.btn_6.clicked.connect(self.logout)

        self.active_button = self.btn_1
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
        self.bondpaper_label = QLabel(str(self.bondpaper_quantity))
        # Connect bondpaper_quantity_updated signal to update_label_slot
        self.bondpaper_quantity_updated.connect(self.update_label_slot)
        bondpaper_layout.addWidget(bondpaper_img)
        bondpaper_layout.addWidget(self.bondpaper_label)

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

        self.btn_1 = CustomButton("Dashboard", "./img/static/dashboard.png", self)
        self.btn_1.setFixedHeight(80)
        self.btn_2 = CustomButton("Add Forms", "./img/static/add_form.png", self)
        self.btn_2.setFixedHeight(80)
        self.btn_3 = CustomButton("Edit Forms", "./img/static/edit_form.png", self)
        self.btn_3.setFixedHeight(80)
        self.btn_4 = CustomButton("Delete Forms", "./img/static/delete_form.png", self)
        self.btn_4.setFixedHeight(80)
        self.btn_5 = CustomButton("Settings", "./img/static/settings.png", self)
        self.btn_5.setFixedHeight(80)
        self.btn_6 = CustomButton("Logout", "./img/static/logout.png", self)
        self.btn_6.setFixedHeight(80)

        self.btn_1.setStyleSheet(
            """
            QPushButton {
                border: none;
                background-color: #D8C995;
                border-radius: 10px;
            }
            """
        )

        default_btn_css = """
            QPushButton {
                border: none;
                border-radius: 10px;
                background-color: transparent;
            }
        """

        self.btn_2.setStyleSheet(default_btn_css)
        self.btn_3.setStyleSheet(default_btn_css)
        self.btn_4.setStyleSheet(default_btn_css)
        self.btn_5.setStyleSheet(default_btn_css)
        self.btn_6.setStyleSheet(default_btn_css)

        self.left_layout = QVBoxLayout()
        self.sidebar_buttons = [
            self.btn_1,
            self.btn_2,
            self.btn_3,
            self.btn_4,
            self.btn_5,
            self.btn_6,
        ]

        for button in self.sidebar_buttons:
            self.left_layout.addWidget(button)

        self.left_layout.addStretch(5)
        self.left_layout.setSpacing(20)
        left_widget = QWidget()
        left_widget.setLayout(self.left_layout)
        left_widget.setFixedWidth(250)

        self.right_widget = QTabWidget()
        self.right_widget.tabBar().setObjectName("mainTab")

        self.right_widget.addTab(self.tab1, "")
        self.right_widget.addTab(self.tab2, "")
        self.right_widget.addTab(self.tab3, "")
        self.right_widget.addTab(self.tab4, "")
        self.right_widget.addTab(self.tab5, "")
        self.right_widget.addTab(self.tab6, "")

        self.right_widget.setCurrentIndex(0)
        self.right_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #B3B3B3;
                border-radius: 25px; /* Adjust the border-radius value as needed */
                padding: 5px;
                background-color: rgba(179, 179, 179, 0.2);
            }
            QTabBar::tab {
                width: 0;
                height: 0;
                margin: 0;
                padding: 0;
                border: none;
            }
            """
        )

        separator = QFrame()  # Create a vertical line separator
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(separator)  # Add the separator to the layout
        main_layout.addWidget(self.right_widget)
        main_layout.setStretch(0, 1)  # Set the stretch factor for left_widget
        main_layout.setStretch(1, 0)  # Set the stretch factor for the separator
        main_layout.setStretch(2, 5)  # Set the stretch factor for right_widget

        layout.addLayout(main_layout)

    # -----------------
    # buttons

    def button1(self):
        self.active_button = self.btn_1
        self.right_widget.setCurrentIndex(0)
        self.update_button_styles()

    def button2(self):
        self.active_button = self.btn_2
        self.right_widget.setCurrentIndex(1)
        self.update_button_styles()

    def button3(self):
        self.active_button = self.btn_3
        self.right_widget.setCurrentIndex(2)
        self.update_button_styles()

    def button4(self):
        self.active_button = self.btn_4
        self.right_widget.setCurrentIndex(3)
        self.update_button_styles()

    def button5(self):
        self.active_button = self.btn_5
        self.right_widget.setCurrentIndex(4)
        self.update_button_styles()

    # -----------------
    # pages

    def ui1(self):
        main_layout = QVBoxLayout()

        title_label = QLabel("Dashboard")
        title_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 28px;
            font-weight: bold;
            color: #19323C;
            margin-top: 10px;
            margin-left: 8px;
            """
        )
        main_layout.addWidget(title_label)
        main_layout.addSpacerItem(
            QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        dashboard_layout = QHBoxLayout()
        
        # Create a QGraphicsDropShadowEffect
        shadow_effect1 = QGraphicsDropShadowEffect()
        shadow_effect1.setBlurRadius(50)
        shadow_effect1.setColor(Qt.gray)
        shadow_effect1.setOffset(0, 0)  # Adjust the shadow's offset as needed
        
        # Create a QGraphicsDropShadowEffect
        shadow_effect2 = QGraphicsDropShadowEffect()
        shadow_effect2.setBlurRadius(50)
        shadow_effect2.setColor(Qt.gray)
        shadow_effect2.setOffset(0, 0)  # Adjust the shadow's offset as needed
        
        # Create a QGraphicsDropShadowEffect
        shadow_effect3 = QGraphicsDropShadowEffect()
        shadow_effect3.setBlurRadius(50)
        shadow_effect3.setColor(Qt.gray)
        shadow_effect3.setOffset(0, 0)  # Adjust the shadow's offset as needed
        
        # Create a QGraphicsDropShadowEffect
        shadow_effect4 = QGraphicsDropShadowEffect()
        shadow_effect4.setBlurRadius(50)
        shadow_effect4.setColor(Qt.gray)
        shadow_effect4.setOffset(0, 0)  # Adjust the shadow's offset as needed

        total_form_widget = TotalFormWidget()

        # Apply the effect to the rectangle
        total_form_widget.setGraphicsEffect(shadow_effect1)
        total_form_widget.setFixedSize(400, 140)
        dashboard_layout.addWidget(total_form_widget)

        total_amount_widget = TotalAmountWidget()
        
        # Apply the effect to the rectangle
        total_amount_widget.setGraphicsEffect(shadow_effect2)
        total_amount_widget.setFixedSize(400, 140)
        dashboard_layout.addWidget(total_amount_widget)

        total_success_widget = TotalSuccessWidget()
        
        # Apply the effect to the rectangle
        total_success_widget.setGraphicsEffect(shadow_effect3)
        total_success_widget.setFixedSize(240, 140)
        dashboard_layout.addWidget(total_success_widget)

        total_failed_widget = TotalFailedWidget()
        
        # Apply the effect to the rectangle
        total_failed_widget.setGraphicsEffect(shadow_effect4)
        total_failed_widget.setFixedSize(240, 140)
        dashboard_layout.addWidget(total_failed_widget)

        dashboard_layout.setAlignment(Qt.AlignLeft)
        main_layout.addLayout(dashboard_layout)

        main_layout.addSpacerItem(
            QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        # Create a table
        self.tableWidget = QTableWidget()
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.verticalHeader().setDefaultSectionSize(80)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.tableWidget)
        main_layout.addLayout(table_layout)

        self.populate_table()

        self.tableWidget.setStyleSheet(
            """
            QTableWidget {
                background-color: #f0f0f0;
                alternate-background-color: #e0e0e0; /* Alternating row color */
                color: #000000;
                border: none;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px; /* Adjust cell padding */
            }
            QTableWidget::item:selected {
                background-color: #e0e0e0; /* Selected item color */
                color: #000000;
            }
            QTableView QTableCornerButton::section {
                background: #7C2F3E;
            }
            QHeaderView::section {
                background-color: #7C2F3E; /* Header background color */
                color: #FAEBD7;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 16px;
            }
        """
        )

        self.selection_enabled = True
        self.tableWidget.clicked.connect(self.clear_selection)

        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui2(self):
        main_layout = QVBoxLayout()

        add_label = QLabel("Add School Forms")
        add_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 28px;
            font-weight: bold;
            color: #19323C;
            margin-top: 10px;
            margin-left: 8px;
            """
        )

        main_layout.addWidget(add_label)

        main_layout.addSpacerItem(
            QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        self.form_widget = FormWidget()
        self.form_widget.title_input_clicked.connect(
            lambda: self.show_virtual_keyboard(self.form_widget.title_input)
        )
        self.form_widget.description_input_clicked.connect(
            lambda: self.show_virtual_keyboard(self.form_widget.description_input)
        )
        self.form_widget.add_button_clicked.connect(self.re_init)

        main_layout.addWidget(self.form_widget)

        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui3(self):
        main_layout = QVBoxLayout()
        edit_label = QLabel("Edit School Forms")
        edit_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 28px;
            font-weight: bold;
            color: #19323C;
            margin-top: 10px;
            margin-left: 8px;
            """
        )

        main_layout.addWidget(edit_label)
        main_layout.addSpacerItem(
            QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        button_labels = self.fetch_button_labels()

        self.vbox_layout = QVBoxLayout()

        for (
            id_num,
            form_name,
            number_of_pages,
            form_description,
            form_category,
        ) in zip(
            button_labels["id_num"],
            button_labels["form_names"],
            button_labels["num_of_pages"],
            button_labels["form_description"],
            button_labels["form_category"],
        ):
            self.button_widget = EditButtonWidget(
                id_num, form_name, str(number_of_pages), form_description, form_category
            )
            self.button_widget.setFixedHeight(220)
            self.button_widget.setFixedWidth(750)
            self.button_widget.setStyleSheet(
                """
                    background-color: #FFFFFF;
                    border-radius: 15px
                """
            )
            self.vbox_layout.addWidget(self.button_widget)

            # Connect the buttonClicked signal to the handleButtonClicked slot
            self.button_widget.buttonClicked.connect(self.edit_form)

        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedSize(880, 785)
        scroll_widget = QWidget()  # Create a widget to hold the grid layout
        scroll_widget.setStyleSheet("background-color: transparent;")

        scroll_area_layout = QVBoxLayout(scroll_widget)
        scroll_area_layout.addLayout(self.vbox_layout)
        scroll_area_layout.setContentsMargins(0, 0, 0, 0)

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

        main_layout.addWidget(scroll_area, alignment=Qt.AlignCenter)

        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui4(self):
        main_layout = QVBoxLayout()
        delete_label = QLabel("Delete School Forms")
        delete_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 28px;
            font-weight: bold;
            color: #19323C;
            margin-top: 10px;
            margin-left: 8px;
            """
        )

        main_layout.addWidget(delete_label)

        main_layout.addSpacerItem(
            QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )

        button_labels = self.fetch_button_labels()

        self.vbox_layout = QVBoxLayout()

        for (
            id_num,
            form_name,
            number_of_pages,
            form_description,
            form_category,
        ) in zip(
            button_labels["id_num"],
            button_labels["form_names"],
            button_labels["num_of_pages"],
            button_labels["form_description"],
            button_labels["form_category"],
        ):
            self.button_widget = DeleteButtonWidget(
                id_num, form_name, str(number_of_pages), form_description, form_category
            )
            self.button_widget.setFixedHeight(220)
            self.button_widget.setFixedWidth(750)
            self.button_widget.setStyleSheet(
                """
                    background-color: #FFFFFF;
                    border-radius: 15px
                """
            )
            self.vbox_layout.addWidget(self.button_widget)

            # Connect the buttonClicked signal to the handleButtonClicked slot
            self.button_widget.delete_button_clicked.connect(self.handleButtonClicked)

        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedSize(880, 785)
        scroll_widget = QWidget()  # Create a widget to hold the grid layout
        scroll_widget.setStyleSheet("background-color: transparent;")

        scroll_area_layout = QVBoxLayout(scroll_widget)
        scroll_area_layout.addLayout(self.vbox_layout)
        scroll_area_layout.setContentsMargins(0, 0, 0, 0)

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

        main_layout.addWidget(scroll_area, alignment=Qt.AlignCenter)

        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui5(self):
        main_layout = QVBoxLayout()

        settings_label = QLabel("Settings")
        settings_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 28px;
            font-weight: bold;
            color: #19323C;
            margin-top: 10px;
            margin-left: 8px;
            """
        )

        main_layout.addWidget(settings_label)

        # Create a QGraphicsDropShadowEffect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(50)
        shadow_effect.setColor(Qt.gray)
        shadow_effect.setOffset(0, 0)  # Adjust the shadow's offset as needed

        # Create a vertical layout to center the frames vertically
        center_layout = QVBoxLayout()
        center_layout.addStretch(1)  # Add stretch to center vertically

        frames_layout = QHBoxLayout()
        frames_layout.setSpacing(100)

        # Create the first frame
        frame1 = QFrame()
        frame1.setFixedSize(500, 680)
        frame1.setStyleSheet(
            """
            background-color: #FFFFFF;
            border-radius: 25px;
            """
        )
        frame1.setGraphicsEffect(shadow_effect)
        frame1_layout = QVBoxLayout(frame1)

        # Add label and buttons to the first frame
        bondpaper_quantity_label = QLabel("Bondpaper Quantity")
        bondpaper_quantity_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-weight: bold;
            font-size: 24px;
            color: #19323C;
            margin-top: 35px;
        """
        )
        frame1_layout.addWidget(bondpaper_quantity_label, alignment=Qt.AlignCenter)

        self.number_value = 10
        self.number_label = QLabel(str(self.number_value))
        self.number_label.setStyleSheet(
            """
            font-family: Roboto;
            font-weight: bold;
            color: #19323C;
            font-size: 124px;
        """
        )
        self.number_label.setContentsMargins(0, 0, 12, 65)
        frame1_layout.addWidget(self.number_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()

        bondpaper_decrement_button = QPushButton("-")
        bondpaper_decrement_button.setStyleSheet(
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
        bondpaper_decrement_button.setFixedSize(65, 65)

        refill_button = QPushButton("Refill")
        refill_button.setStyleSheet(
            """
            QPushButton {
                background-color: #D8C995;
                border: none;
                color: #19323C;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:pressed {
                background-color: #7C2F3E;
                color: #FAEBD7;
            }
            """
        )
        refill_button.setFixedSize(215, 65)

        bondpaper_increment_button = QPushButton("+")
        bondpaper_increment_button.setStyleSheet(
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
        bondpaper_increment_button.setFixedSize(65, 65)

        bondpaper_decrement_button.clicked.connect(self.bondpaper_decrement_value)
        refill_button.clicked.connect(self.refill_bondpaper)
        bondpaper_increment_button.clicked.connect(self.bondpaper_increment_value)

        button_layout.addWidget(bondpaper_decrement_button)
        button_layout.addWidget(refill_button)
        button_layout.addWidget(bondpaper_increment_button)

        button_layout.setContentsMargins(35, 0, 35, 125)

        frame1_layout.addLayout(button_layout)

        # Set size policy of the first frame
        frame1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add the first frame to the frames layout
        frames_layout.addWidget(frame1)

        # Create the second frame
        frame2 = QFrame()
        frame2.setFixedSize(500, 680)
        frame2.setStyleSheet(
            """
            background-color: #FFFFFF;
            border-radius: 25px;
            """
        )
        frame2.setGraphicsEffect(shadow_effect)
        frame2_layout = QVBoxLayout(frame2)

        # Add label and buttons to the second frame
        price_label = QLabel("Base Price")
        price_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-weight: bold;
            font-size: 24px;
            color: #19323C;
            margin-top: 35px;
            """
        )
        frame2_layout.addWidget(price_label, alignment=Qt.AlignCenter)

        self.price_value = 2
        self.quantity_value_label = QLabel(f"₱{self.price_value:0.2f}")
        self.quantity_value_label.setStyleSheet(
            """
            font-family: Roboto;
            font-weight: bold;
            font-size: 124px;
            color: #19323C;
            """
        )
        self.quantity_value_label.setContentsMargins(0, 0, 0, 65)
        frame2_layout.addWidget(self.quantity_value_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()

        price_decrement_button = QPushButton("-")
        price_decrement_button.setStyleSheet(
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
        price_decrement_button.setFixedSize(65, 65)

        change_price_button = QPushButton("Change Price")
        change_price_button.setStyleSheet(
            """
            QPushButton {
                background-color: #D8C995;
                border: none;
                color: #19323C;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:pressed {
                background-color: #7C2F3E;
                color: #FAEBD7;
            }
            """
        )
        change_price_button.setFixedSize(215, 65)

        price_increment_button = QPushButton("+")
        price_increment_button.setStyleSheet(
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
        price_increment_button.setFixedSize(65, 65)

        price_decrement_button.clicked.connect(self.price_decrement_value)
        change_price_button.clicked.connect(self.change_price)
        price_increment_button.clicked.connect(self.price_increment_value)

        button_layout.addWidget(price_decrement_button)
        button_layout.addWidget(change_price_button)
        button_layout.addWidget(price_increment_button)

        button_layout.setContentsMargins(35, 0, 35, 125)

        frame2_layout.addLayout(button_layout)

        # Set size policy of the second frame
        frame2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add the second frame to the frames layout
        frames_layout.addWidget(frame2)

        frames_layout.setAlignment(Qt.AlignCenter)

        # Add frames layout to the centered layout
        center_layout.addLayout(frames_layout)
        center_layout.addStretch(1)  # Add stretch to center vertically

        main_layout.addLayout(center_layout)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def switch_ui(self, index, id_num, form_name):
        self.update_temp_values(id_num, form_name)
        self.right_widget.setCurrentIndex(index)

    def ui6(self):
        main_layout = QVBoxLayout()

        edit_form_label = QLabel("Edit School Forms")
        edit_form_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 28px;
            font-weight: bold;
            color: #19323C;
            margin-top: 10px;
            margin-left: 8px;
            """
        )
        main_layout.addWidget(edit_form_label)

        main_layout.addSpacerItem(
            QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        )
        self.edit_form_widget = EditFormWidget(self.id_num, self.form_name)
        self.edit_form_widget.title_input_clicked.connect(
            lambda: self.show_virtual_keyboard(self.edit_form_widget.title_input)
        )
        self.edit_form_widget.description_input_clicked.connect(
            lambda: self.show_virtual_keyboard(self.edit_form_widget.description_input)
        )
        self.edit_form_widget.edit_form_success.connect(self.re_init)
        main_layout.addWidget(self.edit_form_widget)

        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def update_button_styles(self):
        # Reset style for all buttons
        for button in self.sidebar_buttons:
            button.setStyleSheet(
                """
                QPushButton {
                    border: none;
                    border-radius: 10px;
                    background-color: transparent;
                }
                """
            )

        # Set active button style
        self.active_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                background-color: #D8C995;
                border-radius: 10px;
            }
            """
        )

    def show_virtual_keyboard(self, title_input):
        self.virtual_keyboard.display(title_input)

    def bondpaper_increment_value(self):
        self.number_value += 10
        self.number_label.setText(str(self.number_value))

    def bondpaper_decrement_value(self):
        if self.number_value > 10:
            self.number_value -= 10
            self.number_label.setText(str(self.number_value))

    def price_increment_value(self):
        self.price_value += 1
        self.quantity_value_label.setText(f"₱{self.price_value:0.2f}")

    def price_decrement_value(self):
        if self.price_value > 1:
            self.price_value -= 1
            self.quantity_value_label.setText(f"₱{self.price_value:0.2f}")

    def change_price(self):
        new_price = self.price_value

        try:
            connection = sqlite3.connect("kiosk.db")
            cursor = connection.cursor()

            cursor.execute("BEGIN TRANSACTION")

            cursor.execute(
                """
                UPDATE kiosk_settings
                SET base_price = ?
                WHERE ROWID = (
                    SELECT ROWID
                    FROM kiosk_settings
                    ORDER BY ROWID
                    LIMIT 1
                )
            """,
                (new_price,),
            )

            cursor.execute("COMMIT")

            cursor.execute("SELECT base_price FROM kiosk_settings LIMIT 1")
            self.base_price = cursor.fetchone()[0]

            print(self.base_price)
            print("Price changed successfully.")

            # Display dialog box indicating success
            message_box = CustomMessageBox(
                "Success", "Price changed successfully.", parent=self
            )
            message_box.exec_()

        except sqlite3.Error as error:
            connection.rollback()
            print("Error changing price:", error)

        finally:
            if connection:
                connection.close()

    def refill_bondpaper(self):
        bondpaper_quantity = self.number_value

        try:
            connection = sqlite3.connect("kiosk.db")
            cursor = connection.cursor()

            cursor.execute("BEGIN TRANSACTION")

            cursor.execute(
                """
                UPDATE kiosk_settings
                SET bondpaper_quantity = bondpaper_quantity + ?
                WHERE ROWID = (
                    SELECT ROWID
                    FROM kiosk_settings
                    ORDER BY ROWID
                    LIMIT 1
                )
            """,
                (bondpaper_quantity,),
            )

            cursor.execute("COMMIT")

            cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
            self.bondpaper_quantity = cursor.fetchone()[0]

            print(self.bondpaper_quantity)
            print("Bondpaper refilled successfully.")

            # Emit signal to update label
            self.bondpaper_quantity_updated.emit(self.bondpaper_quantity)

            # Display dialog box indicating success
            message_box = CustomMessageBox(
                "Success", "Bondpaper refilled successfully.", parent=self
            )
            message_box.exec_()

        except sqlite3.Error as error:
            connection.rollback()
            print("Error changing price:", error)

        finally:
            if connection:
                connection.close()

    # Slot to update the bondpaper label
    def update_label_slot(self, new_quantity):
        self.bondpaper_label.setText(str(new_quantity))

    def populate_table(self):
        try:
            connection = sqlite3.connect("kiosk.db")
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM kiosk_print_results")
            data = cursor.fetchall()

            column_names = [
                self.format_column_name(description[0])
                for description in cursor.description
            ]

            self.tableWidget.setColumnCount(len(column_names))
            self.tableWidget.setHorizontalHeaderLabels(column_names)

            self.tableWidget.setRowCount(len(data))
            for row_num, row_data in enumerate(data):
                for row_num, row_data in enumerate(data):
                    for col_num, col_data in enumerate(row_data):
                        item = QTableWidgetItem(str(col_data))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tableWidget.setItem(row_num, col_num, item)

            header = self.tableWidget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)

        except sqlite3.Error as error:
            print("Error populating table:", error)

        finally:
            if connection:
                connection.close()

    def format_column_name(self, column_name):
        # Split the column name by underscores
        words = column_name.split("_")
        # Capitalize the first letter of each word
        words = [word.capitalize() for word in words]
        # Join the words with spaces
        return " ".join(words)

    def clear_selection(self):
        # Toggle the selection state
        self.selection_enabled = not self.selection_enabled

        if not self.selection_enabled:
            # Clear the selection if selection is disabled
            self.tableWidget.clearSelection()

    def fetch_button_labels(self):
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, form_name, number_of_pages, form_description, form_category FROM kiosk_forms"
        )
        rows = cursor.fetchall()

        conn.close()

        id_num = []
        form_names = []
        num_of_pages = []
        form_description = []
        form_category = []

        for row in rows:
            id_num.append(row[0])
            form_names.append(row[1])
            num_of_pages.append(row[2])
            form_description.append(row[3])
            form_category.append(row[4])

        # Create a dictionary to store the lists
        button_labels = {
            "id_num": id_num,
            "form_names": form_names,
            "num_of_pages": num_of_pages,
            "form_description": form_description,
            "form_category": form_category,
        }

        return button_labels

    def handleButtonClicked(self, index, form_name):
        print(index)
        print(form_name)

        self.delete_message_box = DeleteMessageBox(index, form_name, parent=self)
        self.delete_message_box.continue_button_clicked.connect(self.delete_form)
        self.delete_message_box.exec_()

    def delete_form(self, index, form_name):
        button_widget = self.sender()
        # Remove the button widget from the layout
        self.vbox_layout.removeWidget(button_widget)
        button_widget.deleteLater()

        try:
            conn = sqlite3.connect("kiosk.db")
            cursor = conn.cursor()

            cursor.execute("DELETE FROM kiosk_forms WHERE id = ?", (index,))

            conn.commit()  # Commit changes to the database
            conn.close()

            self.re_init()

            message_box = CustomMessageBox(
                "Success",
                f"{form_name} deleted successfully!",
                parent=self,
            )
            message_box.exec_()

        except sqlite3.Error as e:
            print("Error deleting row:", e)

    def edit_form(self, index, form_name):
        self.edit_message_box = EditMessageBox(index, form_name, parent=self)
        self.edit_message_box.edit_form_button_clicked.connect(self.switch_ui)
        self.edit_message_box.exec_()

    def update_temp_values(self, index, form_name):
        self.id_num = index
        self.form_name = form_name
        print(self.form_name)
        # Update UI to reflect new values
        self.tab1 = self.ui1()
        self.tab2 = self.ui2()
        self.tab3 = self.ui3()
        self.tab4 = self.ui4()
        self.tab5 = self.ui5()
        self.tab6 = self.ui6()
        self.right_widget.clear()
        self.right_widget.addTab(self.tab1, "")
        self.right_widget.addTab(self.tab2, "")
        self.right_widget.addTab(self.tab3, "")
        self.right_widget.addTab(self.tab4, "")
        self.right_widget.addTab(self.tab5, "")
        self.right_widget.addTab(self.tab6, "")

    def re_init(self):
        # Update UI to reflect new values
        self.tab1 = self.ui1()
        self.tab2 = self.ui2()
        self.tab3 = self.ui3()
        self.tab4 = self.ui4()
        self.tab5 = self.ui5()
        self.tab6 = self.ui6()
        self.right_widget.clear()
        self.right_widget.addTab(self.tab1, "")
        self.right_widget.addTab(self.tab2, "")
        self.right_widget.addTab(self.tab3, "")
        self.right_widget.addTab(self.tab4, "")
        self.right_widget.addTab(self.tab5, "")
        self.right_widget.addTab(self.tab6, "")

    def logout(self):
        self.setVisible(False)
        self.home_screen_backbt_clicked.emit()
