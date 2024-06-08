import os
import sys
import cups
import time
import sqlite3
import datetime
from PyQt5.QtWidgets import (
    QApplication,
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
    QStyledItemDelegate,
    QListView,
    QTextBrowser,
    QGridLayout,
)
from PyQt5.QtCore import (
    Qt,
    QTimer,
    QThread,
    QPropertyAnimation,
    QEasingCurve,
    pyqtSignal,
    pyqtSlot,
)
from PyQt5.QtGui import QPixmap, QMovie, QColor
from virtual_keyboard import AlphaNeumericVirtualKeyboard
from helpers import (
    upload_form_file,
    upload_process_file,
    edit_form_file,
    edit_process_file,
    delete_form_file,
    delete_process_file,
    delete_form_preview,
)
from custom_message_box import CustomMessageBox


class SmoothScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalScrollBar().setSingleStep(15)  # Set the scrolling step size
        self._mousePressPos = None
        self._scrollBarValueAtMousePress = None
        self._animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._animation.setEasingCurve(QEasingCurve.OutQuad)
        self._animation.setDuration(500)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mousePressPos = event.globalPos()
            self._scrollBarValueAtMousePress = self.verticalScrollBar().value()
            self._animation.stop()  # Stop any ongoing animation when the user interacts
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._mousePressPos:
            delta = event.globalPos() - self._mousePressPos
            self.verticalScrollBar().setValue(
                self._scrollBarValueAtMousePress - delta.y()
            )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._mousePressPos:
            delta = event.globalPos() - self._mousePressPos
            target_value = self._scrollBarValueAtMousePress - delta.y()
            self.smoothScrollTo(target_value)
        self._mousePressPos = None
        self._scrollBarValueAtMousePress = None
        super().mouseReleaseEvent(event)

    def smoothScrollTo(self, target_value):
        self._animation.setStartValue(self.verticalScrollBar().value())
        self._animation.setEndValue(target_value)
        self._animation.start()


class MessageBox(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 240)

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
        message_label.setStyleSheet("font-size: 16px; font-family: Roboto; ")
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
        message_label.setStyleSheet("font-size: 16px; font-family: Roboto; ")
        layout.addWidget(message_label, alignment=Qt.AlignCenter)

        scroll_layout = QHBoxLayout()
        layout.addLayout(scroll_layout)

        file_button = QPushButton("Discard")
        file_button.setFocusPolicy(Qt.NoFocus)
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
        scroll_layout.addWidget(file_button, alignment=Qt.AlignCenter)

        form_file_button = QPushButton("Continue")
        form_file_button.setFocusPolicy(Qt.NoFocus)
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
        scroll_layout.addWidget(form_file_button, alignment=Qt.AlignCenter)
        scroll_layout.setContentsMargins(45, 0, 65, 0)

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
        message_label.setStyleSheet("font-size: 16px; font-family: Roboto; ")
        layout.addWidget(message_label, alignment=Qt.AlignCenter)

        scroll_layout = QHBoxLayout()
        layout.addLayout(scroll_layout)

        discard_button = QPushButton("Discard")
        discard_button.setFocusPolicy(Qt.NoFocus)
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
        scroll_layout.addWidget(discard_button, alignment=Qt.AlignCenter)

        continue_button = QPushButton("Continue")
        continue_button.setFocusPolicy(Qt.NoFocus)
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
        scroll_layout.addWidget(continue_button, alignment=Qt.AlignCenter)
        scroll_layout.setContentsMargins(55, 0, 65, 0)

    def continue_clicked(self):
        self.continue_button_clicked.emit(self.index, self.form_name)
        self.accept()


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


class CustomDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        # Increase the height (for example, make it double)
        size.setHeight(size.height() * 3)
        return size

    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        # Draw separator line
        if index.row() < option.widget.model().rowCount() - 1:
            rect = option.rect
            painter.save()
            pen = painter.pen()
            pen.setColor(QColor("#B3B3B3"))
            painter.setPen(pen)
            painter.drawLine(rect.bottomLeft(), rect.bottomRight())
            painter.restore()


class FormWidget(QWidget):
    title_input_clicked = pyqtSignal()
    description_input_clicked = pyqtSignal()
    add_button_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
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
        self.form_category = [
            "Accreditation",
            "Clearance",
            "Enrollment",
            "Graduation",
            "Petition",
            "Research",
            "Other",
        ]
        self.category_input.addItems(self.form_category)
        self.category_input.setFixedWidth(300)

        view = QListView()
        self.category_input.setView(view)

        delegate = CustomDelegate()
        self.category_input.setItemDelegate(delegate)

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
        self.add_button.setFocusPolicy(Qt.NoFocus)
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
        self.clear_button.setFocusPolicy(Qt.NoFocus)
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
            conn = sqlite3.connect("./database/kiosk.db")
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
        self.form_name = form_name

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
        self.form_category = [
            "Accreditation",
            "Clearance",
            "Enrollment",
            "Graduation",
            "Petition",
            "Research",
            "Other",
        ]
        self.category_input.addItems(self.form_category)
        self.category_input.setFixedWidth(300)

        view = QListView()
        self.category_input.setView(view)

        delegate = CustomDelegate()
        self.category_input.setItemDelegate(delegate)

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
        self.add_button = QPushButton("Edit")
        self.add_button.setFocusPolicy(Qt.NoFocus)
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
        self.clear_button.setFocusPolicy(Qt.NoFocus)
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
            conn = sqlite3.connect("./database/kiosk.db")
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
            edit_form_file(form_file_path, form_title, self.form_name)

            process_file_path = self.upload_process_widget.get_file()
            edit_process_file(process_file_path, form_title, self.form_name)

            self.edit_form_success.emit()

            message_box = CustomMessageBox(
                "Success",
                f"{form_title} has been successfully updated.",
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
        self.browse_button.setFocusPolicy(Qt.NoFocus)
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
        # Create a QFileDialog instance
        dialog = QFileDialog(self, "Open File", "/media/amarjeet/", "Document (*.pdf)")

        # Set the options for the dialog
        dialog.setOptions(QFileDialog.DontUseNativeDialog)

        # Adjust the size of the QFileDialog
        dialog.resize(800, 600)  # Width: 800, Height: 600

        # Execute the dialog and get the selected file path
        if dialog.exec_() == QFileDialog.Accepted:
            file_path = dialog.selectedFiles()[0]
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
        self.browse_button.setFocusPolicy(Qt.NoFocus)
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
        dialog = QFileDialog(
            self, "Open File", "/media/amarjeet/", "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        # Set the options for the dialog
        dialog.setOptions(QFileDialog.DontUseNativeDialog)

        # Adjust the size of the QFileDialog
        dialog.resize(800, 600)  # Width: 800, Height: 600

        if dialog.exec_() == QFileDialog.Accepted:
            file_path = dialog.selectedFiles()[0]
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
            font-family: Roboto; 
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
    daily_selected = pyqtSignal(float)
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
        self.action1 = QAction("Daily", self)
        self.action2 = QAction("Weekly", self)
        self.action3 = QAction("Monthly", self)
        self.action4 = QAction("Yearly", self)

        # Connect actions to their respective slots
        self.action1.triggered.connect(self.sort_daily)
        self.action2.triggered.connect(self.sort_weekly)
        self.action3.triggered.connect(self.sort_monthly)
        self.action4.triggered.connect(self.sort_yearly)

        # Add actions to the menu
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)

        self.setMenu(self.menu)
        self.setFocusPolicy(Qt.NoFocus)

        # Set initial state to "Weekly"
        self.setText("Daily")
        self.sort_daily()

    def sort_daily(self):
        self.setText("Daily")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        # Get the current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Execute the SQL query to sum the total amount based on the current date
        cursor.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0) AS total_amount
            FROM kiosk_print_results
            WHERE date(date_printed) = ? AND result = 'Success'
            """,
            (current_date,),
        )

        # Fetch the result
        self.total_amount = cursor.fetchone()[0]

        # Close the cursor and database connection
        cursor.close()
        conn.close()

        self.daily_selected.emit(self.total_amount)

    def get_daily_amount(self):
        return float(self.total_amount)

    def sort_weekly(self):
        self.setText("Weekly")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
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

    def sort_monthly(self):
        self.setText("Monthly")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
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
        conn = sqlite3.connect("./database/kiosk.db")
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
    daily_selected = pyqtSignal(str)
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
        self.action1 = QAction("Daily", self)
        self.action2 = QAction("Weekly", self)
        self.action3 = QAction("Monthly", self)
        self.action4 = QAction("Yearly", self)

        # Connect actions to their respective slots
        self.action1.triggered.connect(self.sort_daily)
        self.action2.triggered.connect(self.sort_weekly)
        self.action3.triggered.connect(self.sort_monthly)
        self.action4.triggered.connect(self.sort_yearly)

        # Add actions to the menu
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)

        self.setMenu(self.menu)
        self.setFocusPolicy(Qt.NoFocus)

        # Set initial state to "Weekly"
        self.setText("Daily")
        self.sort_daily()

    def sort_daily(self):
        self.setText("Daily")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        # Get the start and end dates for the current day
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            SELECT COALESCE(
                    (SELECT form_name
                        FROM kiosk_print_results
                        WHERE strftime('%Y-%m-%d', date_printed) = ? 
                            AND result = 'Success'
                        GROUP BY form_name
                        ORDER BY SUM(number_of_copies) DESC
                        LIMIT 1
                    ), 'None'
                )
        """,
            (current_date,),
        )

        self.total_form = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.daily_selected.emit(self.total_form)

    def get_daily_amount(self):
        return self.total_form

    def sort_weekly(self):
        self.setText("Weekly")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
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

    def sort_monthly(self):
        self.setText("Monthly")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
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
        conn = sqlite3.connect("./database/kiosk.db")
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
    daily_selected = pyqtSignal(int)
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
        self.action1 = QAction("Daily", self)
        self.action2 = QAction("Weekly", self)
        self.action3 = QAction("Monthly", self)
        self.action4 = QAction("Yearly", self)

        # Connect actions to their respective slots
        self.action1.triggered.connect(self.sort_daily)
        self.action2.triggered.connect(self.sort_weekly)
        self.action3.triggered.connect(self.sort_monthly)
        self.action4.triggered.connect(self.sort_yearly)

        # Add actions to the menu
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)

        self.setMenu(self.menu)
        self.setFocusPolicy(Qt.NoFocus)

        # Set initial state to "Weekly"
        self.setText("Daily")
        self.sort_daily()

    def sort_daily(self):
        self.setText("Daily")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        # Get the start and end dates for the current day
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            SELECT COUNT(*) AS total_failed_count
            FROM kiosk_print_results
            WHERE result = 'Failed'
            AND date(date_printed) = ?
        """,
            (current_date,),
        )

        self.total_error = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.daily_selected.emit(self.total_error)

    def get_daily_amount(self):
        return self.total_error

    def sort_weekly(self):
        self.setText("Weekly")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
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

    def sort_monthly(self):
        self.setText("Monthly")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
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
        conn = sqlite3.connect("./database/kiosk.db")
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
    daily_selected = pyqtSignal(int)
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
        self.action1 = QAction("Daily", self)
        self.action2 = QAction("Weekly", self)
        self.action3 = QAction("Monthly", self)
        self.action4 = QAction("Yearly", self)

        # Connect actions to their respective slots
        self.action1.triggered.connect(self.sort_daily)
        self.action2.triggered.connect(self.sort_weekly)
        self.action3.triggered.connect(self.sort_monthly)
        self.action4.triggered.connect(self.sort_yearly)

        # Add actions to the menu
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        self.menu.addAction(self.action4)

        self.setMenu(self.menu)
        self.setFocusPolicy(Qt.NoFocus)

        # Set initial state to "Weekly"
        self.setText("Daily")
        self.sort_daily()

    def sort_daily(self):
        self.setText("Daily")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        # Get the start and end dates for the current day
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            SELECT COUNT(*) AS total_success_count
            FROM kiosk_print_results
            WHERE result = 'Success'
            AND date(date_printed) = ?
        """,
            (current_date,),
        )

        self.total_success = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        self.daily_selected.emit(self.total_success)

    def get_daily_amount(self):
        return self.total_success

    def sort_weekly(self):
        self.setText("Weekly")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
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

    def sort_monthly(self):
        self.setText("Monthly")

        # Connect to the database
        conn = sqlite3.connect("./database/kiosk.db")
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
        conn = sqlite3.connect("./database/kiosk.db")
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

        button.daily_selected.connect(self.change_total_label)
        button.weekly_selected.connect(self.change_total_label)
        button.monthly_selected.connect(self.change_total_label)
        button.yearly_selected.connect(self.change_total_label)

        daily_total = button.get_daily_amount()

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

        self.total_label = QLabel(f"₱ {daily_total}")
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

        button.daily_selected.connect(self.change_total_label)
        button.weekly_selected.connect(self.change_total_label)
        button.monthly_selected.connect(self.change_total_label)
        button.yearly_selected.connect(self.change_total_label)

        daily_total = button.get_daily_amount()

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

        self.total_label = QLabel(f"{daily_total}")
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

        button.daily_selected.connect(self.change_total_label)
        button.weekly_selected.connect(self.change_total_label)
        button.monthly_selected.connect(self.change_total_label)
        button.yearly_selected.connect(self.change_total_label)

        daily_total = button.get_daily_amount()

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

        self.total_label = QLabel(f"{daily_total}")
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

        button.daily_selected.connect(self.change_total_label)
        button.weekly_selected.connect(self.change_total_label)
        button.monthly_selected.connect(self.change_total_label)
        button.yearly_selected.connect(self.change_total_label)

        daily_total = button.get_daily_amount()

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

        self.total_label = QLabel(f"{daily_total}")
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


class HelpMessageButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        scroll_layout = QHBoxLayout()

        self.label = QLabel(title)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(
            """
            font-family: Roboto;
            font-size: 15px;
            background-color: transparent;
            color: #19323C;
            margin-left: 15px;         
            """
        )

        pixmap = QPixmap("./img/static/next_arrow_img.png")
        scaled_pixmap = pixmap.scaled(
            15, 35, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label = QLabel()
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet(
            "margin-right: 15px; background-color: transparent"
        )

        scroll_layout.addWidget(self.label)
        scroll_layout.addWidget(self.image_label, alignment=Qt.AlignRight)

        layout.addLayout(scroll_layout)  # Add scroll_layout to the existing layout

        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:pressed {
                background-color: #FDFDFD;
            }
            """
        )
        self.setFocusPolicy(Qt.NoFocus)
        self.setFixedHeight(65)


class HelpMessageBox(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 900)
        self.setStyleSheet("background-color: #EBEBEB;")
        self.setup_ui()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        upper_layout = QHBoxLayout()
        upper_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        upper_layout.setSpacing(167)

        self.close_button = QPushButton()
        self.close_button.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/static/close_img.png');}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/static/close_img_pressed.png');}"
        )
        self.close_button.setFixedSize(45, 45)
        self.close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.close_button.clicked.connect(self.close_message_box)

        self.help_label = QLabel("Get Help")
        self.help_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 22px;
            color: #19323C;
            """
        )

        upper_layout.addWidget(self.close_button, Qt.AlignLeft)
        upper_layout.addWidget(self.help_label)
        upper_layout.setContentsMargins(8, 15, 0, 0)

        back_layout = QVBoxLayout()

        self.back_button = QPushButton()
        self.back_button.setFixedSize(30, 30)
        self.back_button.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/static/back_img.png');}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/static/back_img_pressed.png');}"
        )
        self.back_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.back_button.clicked.connect(self.go_back)
        self.back_button.hide()

        back_layout.addWidget(self.back_button)
        back_layout.setContentsMargins(15, 20, 0, 20)

        self.help_title_label = QLabel(
            "Admin Guide for Form Handling and System Maintenance"
        )
        self.help_title_label.setWordWrap(True)
        self.help_title_label.setStyleSheet(
            """
            font-family: Roboto;
            font-weight: bold;
            font-size: 24px;
            margin-left: 8px;
            color: #7C2F3E;
            margin-bottom: 15px;
            """
        )

        self.help_text = QTextBrowser()
        self.help_text.setStyleSheet(
            "QTextBrowser { border: none; background: transparent; margin-right: 30px; }"
        )
        self.help_text.setFixedHeight(700)
        self.help_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.help_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.help_text.hide()

        # Scroll area setup
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("border: none")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.how_to_add = HelpMessageButton("How to add form/s?", self)
        self.how_to_edit = HelpMessageButton("How to edit form/s?", self)
        self.how_to_delete = HelpMessageButton("How to delete form/s?", self)
        self.how_to_refill = HelpMessageButton(
            "How to refill the bond paper quantity?", self
        )
        self.how_to_change_price = HelpMessageButton(
            "How to change the base price?", self
        )
        self.total_amount_collected = HelpMessageButton(
            "Where can I see the total amount of collected coins?", self
        )
        self.total_number_forms = HelpMessageButton(
            "Where can I see the total number of printed forms successful and unsuccessful?",
            self,
        )
        self.total_remaining_paper = HelpMessageButton(
            "Where can I see the total of the remaining paper?", self
        )
        self.printer_active = HelpMessageButton(
            "Where can I see to know if the printer is active/connected?", self
        )
        self.track_ink = HelpMessageButton(
            "Where can I see the tracking of the ink of the printer?", self
        )
        self.printer_status_checker = HelpMessageButton(
            "How can I check the printer status using the warning button?", self
        )
        self.go_back_to_interface = HelpMessageButton(
            "How can I go back to the user interface?", self
        )
        self.restart_shutdown = HelpMessageButton(
            "How can I restart or shutdown the kiosk?", self
        )

        self.how_to_add.clicked.connect(self.how_to_add_form)
        self.how_to_edit.clicked.connect(self.how_to_edit_form)
        self.how_to_delete.clicked.connect(self.how_to_delete_form)
        self.how_to_refill.clicked.connect(self.how_to_refill_bondpaper)
        self.how_to_change_price.clicked.connect(self.how_to_change_base_price)
        self.total_amount_collected.clicked.connect(self.total_amount_collected_coins)
        self.total_number_forms.clicked.connect(
            self.total_number_forms_success_unsuccessful
        )
        self.total_remaining_paper.clicked.connect(self.remaining_paper)
        self.printer_active.clicked.connect(self.printer_active_connected)
        self.track_ink.clicked.connect(self.track_ink_printer)
        self.printer_status_checker.clicked.connect(self.status_checker)
        self.go_back_to_interface.clicked.connect(self.go_to_interface)
        self.restart_shutdown.clicked.connect(self.restart_shutdown_kiosk)

        self.lines = []
        self.add_widget_with_line(scroll_layout, self.how_to_add)
        self.add_widget_with_line(scroll_layout, self.how_to_edit)
        self.add_widget_with_line(scroll_layout, self.how_to_delete)
        self.add_widget_with_line(scroll_layout, self.how_to_refill)
        self.add_widget_with_line(scroll_layout, self.how_to_change_price)
        self.add_widget_with_line(scroll_layout, self.total_amount_collected)
        self.add_widget_with_line(scroll_layout, self.total_number_forms)
        self.add_widget_with_line(scroll_layout, self.total_remaining_paper)
        self.add_widget_with_line(scroll_layout, self.printer_active)
        self.add_widget_with_line(scroll_layout, self.track_ink)
        self.add_widget_with_line(scroll_layout, self.printer_status_checker)
        self.add_widget_with_line(scroll_layout, self.go_back_to_interface)
        scroll_layout.addWidget(self.restart_shutdown)
        scroll_layout.setContentsMargins(0, 0, 0, 135)

        scroll_content.setLayout(scroll_layout)
        self.scroll_area.setWidget(scroll_content)

        self.layout.addLayout(upper_layout)
        self.layout.addLayout(back_layout)
        self.layout.addWidget(self.help_title_label)
        self.layout.addWidget(self.help_text)
        self.layout.addWidget(self.scroll_area)

    def how_to_add_form(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText("How to add form/s?")

        html_content = """
        <ol>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Plug in a USB Flash Drive</strong><br>
            Plug in a USB flash drive containing your file of the form or process to be uploaded.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Click the "Add Forms" Button</strong><br>
            To add form(s), click the "Add Forms" button.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Fill Out the Form Information</strong><br>
            Fill out the form information text boxes: [Form Title, Form Category, Number of Pages, Form Description]</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Upload Form File</strong><br>
            To upload form file(s) should be in PDF format. Click the "Browse" button to upload the form. Select the form file from your plugged-in USB flash drive.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Upload Process File</strong><br>
            To upload a process file. Click the "Browse" button for process upload. Select the file from your plugged-in USB flash drive.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Confirm or Discard Changes</strong><br>
            To successfully confirm the changes you've made, click the "Add" button. To discard the changes, click the "Clear" button.</li><br>
        </ol>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def how_to_edit_form(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText("How to edit form/s?")

        html_content = """
        <ol>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Plug in a USB Flash Drive</strong><br>
            Plug in a USB flash drive containing your file of the form or process to be uploaded.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Select the Form to Edit</strong><br>
            Select the form you need or want to edit from the list of forms by scrolling through the list.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Click the "Edit" Button</strong><br>
            Click the "Edit" button to start editing the form. Click the "Continue" button to proceed with making changes. Click the "Discard" button if you do not want to continue with the changes.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Proceed to the Editing Interface</strong><br>
            After clicking the "Continue" button, you will be taken to the same interface as when adding forms.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Fill Out the Form Information</strong><br>
            Fill out the form information text boxes: [Form Title, Form Category, Number of Pages, Form Description]</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Upload Form File</strong><br>
            To upload the form file(s) it should be in PDF format. Click the "Browse" button to upload the form. Select the form file from your plugged-in USB flash drive.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Upload Process File</strong><br>
            To upload a process file. Click the "Browse" button for process upload. Select the file from your plugged-in USB flash drive.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Confirm or Discard Changes</strong><br>
            To successfully confirm the changes you've made, click the "Edit" button. To discard the changes, click the "Clear" button.</li><br>
        </ol>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def how_to_delete_form(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText("How to delete form/s?")

        html_content = """
        <ol>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Select the Form to Delete</strong><br>
            Select the form you need or want to delete from the list of forms by scrolling through the list.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Click the "Delete" Button</strong><br>
            Click the "Delete" button to delete the form. Click the "Continue" button to proceed with deleting the form. Click the "Discard" button if you do not want to delete the form.</li><br>
        </ol>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def how_to_refill_bondpaper(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText("How to refill the bond paper quantity?")

        html_content = """
        <ol>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Click the Settings Button</strong><br>
            Start by clicking the settings button in the system interface.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Add Quantity</strong><br>
            Click the plus sign (+) button to add the quantity of bond paper.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Save Changes</strong><br>
            Click the refill button to save the changes.</li><br>
        </ol>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def how_to_change_base_price(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText("How to change the base price?")

        html_content = """
        <ol>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Increase Base Price:</strong><br>
                <ol style="list-style-type: decimal;">
                    <li style="font-size: 16px; margin-left: 8px;"><strong>Click the plus sign (+) button</strong><br>
                    Click the plus sign (+) button to increase the base price of the form per page.</li><br>
                    <li style="font-size: 16px; margin-left: 8px;"><strong>Click the change price button</strong><br>
                    Click the change price button to save the new price.</li><br>
                </ol>
            </li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Decrease Base Price:</strong><br>
                <ol style="list-style-type: decimal;">
                    <li style="font-size: 16px; margin-left: 8px;"><strong>Click the minus sign (-) button</strong><br>
                    Click the minus sign (-) button to decrease the base price of the form per page.</li><br>
                    <li style="font-size: 16px; margin-left: 8px;"><strong>Click the change price button</strong><br>
                    Click the change price button to save the new price.</li><br>
                </ol>
            </li><br>
        </ol>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def total_amount_collected_coins(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText(
            "Where can I see the total amount of collected coins?"
        )

        html_content = """
        <p style="font-size: 16px; margin-left: 8px;">You can see the total amount of collected 
        coins on the dashboard at the top part of the screen. The dashboard provides a comprehensive view 
        of the total amount of collected coins in various time frames:</p>
        <ul>
            <li style="font-size: 16px; margin-left: 8px;">Daily</li>
            <li style="font-size: 16px; margin-left: 8px;">Weekly</li>
            <li style="font-size: 16px; margin-left: 8px;">Monthly</li>
            <li style="font-size: 16px; margin-left: 8px;">Yearly</li>
        </ul>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def total_number_forms_success_unsuccessful(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText(
            "Where can I see the total number of printed forms successful and unsuccessful?"
        )

        html_content = """
        <p style="font-size: 16px; margin-left: 8px;">You can see the total number of successful and unsuccessful printed 
        forms on the dashboard at the top part of the screen. The dashboard provides a comprehensive view of the total number 
        of printed forms in various time frames:</p>
        <ul>
            <li style="font-size: 16px; margin-left: 8px;">Daily</li>
            <li style="font-size: 16px; margin-left: 8px;">Weekly</li>
            <li style="font-size: 16px; margin-left: 8px;">Monthly</li>
            <li style="font-size: 16px; margin-left: 8px;">Yearly</li>
        </ul>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def remaining_paper(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText(
            "Where can I see the total of the remaining paper?"
        )

        html_content = """
        <p style="font-size: 16px; margin-left: 8px;">You can see the total amount of remaining paper at
        the top right part of the screen. The paper icon serves as the indicator of the remaining paper.</p>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def printer_active_connected(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText(
            "Where can I see to know if the printer is active/connected?"
        )

        html_content = """
        <p style="font-size: 16px; margin-left: 8px;">To know if the printer is active, you can check the printer icon at the top right part of the screen.</p>
        <ul>
            <li style="font-size: 16px; margin-left: 8px;">A check (✓) sign indicates that the printer is active or connected.</li>
            <li style="font-size: 16px; margin-left: 8px;">A cross (✕) sign indicates that the printer is not active or not connected.</li>
        </ul>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def track_ink_printer(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText(
            "Where can I see the tracking of the ink of the printer?"
        )

        html_content = """
        <p style="font-size: 16px; margin-left: 8px;">You can track the printer ink levels using the indicator at the top right part of the screen.</p>
        <ul>
            <li style="font-size: 16px; margin-left: 8px;">A check (✓) sign indicates that the ink level is good.</li>
            <li style="font-size: 16px; margin-left: 8px;">A cross (✕) sign indicates that the ink level is low or not good.</li>
        </ul>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def status_checker(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText(
            "How can I check the printer status using the warning button?"
        )

        html_content = """
        <p style="font-size: 16px; margin-left: 8px;">
            <strong>To check the printer status using the warning button on the admin panel, follow these steps:</strong>
        </p>
        <ol style="font-size: 16px; margin-left: 20px;">
            <li><strong>Locate the Warning Button:</strong><br>
                Navigate to the top right of the screen. Here, you will find the warning button alongside other indicators. The presence of the warning button indicates that the printer is currently not connected.</li>
            <li><strong>Activate the Status Check:</strong><br>
                Click on the warning button. This action will initiate a continuous status check for the printer. The system will automatically refresh the status every 3 seconds.</li>
            <li><strong>Monitor the Status:</strong><br>
                The diagnostic window will provide real-time updates on the printer’s connectivity. Continuously monitor the window until the printer's status changes.</li>
            <li><strong>Status Update:</strong><br>
                When the printer becomes available, the status window will display "Printer is available." At this point, you can close the printer status window, and the warning indicator for the printer at the top right of the screen will disappear.</li>
            <li><strong>Resolve or Restart:</strong><br>
                If the printer status does not resolve or if the issue persists, the administrator has the option to restart or shutdown the kiosk. To do so, the admin can access the appropriate controls, usually located at the bottom left part of the panel. Restarting or shutting down the kiosk can often resolve underlying software issues affecting the printer.</li>
        </ol>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def go_to_interface(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText("How can I go back to the user interface?")

        html_content = """
        <p style="font-size: 16px; margin-left:8px;">To go back to the user interface, click the "Power" button at the lower part of the scree and click the "Logout" button.</p>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def restart_shutdown_kiosk(self):
        self.scroll_area.hide()
        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()
        self.help_title_label.setText("How can I restart or shutdown the kiosk?")

        html_content = """
        <p style="font-size: 16px; margin-left: 8px;">To restart or shutdown the kiosk, click the “Power” button at the lower left part of the screen.</p>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def go_back(self):
        self.scroll_area.show()

        self.close_button.show()
        self.help_label.show()

        self.back_button.hide()

        self.help_title_label.setText(
            "Admin Guide for Form Handling and System Maintenance"
        )
        self.help_text.hide()

    def add_widget_with_line(self, layout, widget):
        layout.addWidget(widget)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("QFrame { border: none; border-bottom: 1px solid #9D9D9D; }")
        layout.addWidget(line)
        self.lines.append(line)  # Store a reference to the line

    def close_message_box(self):
        self.reject()


class PrinterStatus(QThread):
    status_updated = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.printer_state = None
        self.running = True

    def run(self):
        while self.running:
            self.is_printer_available()
            time.sleep(3)

    def is_printer_available(self):
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()

            if not printers:
                self.printer_state = False
            else:
                idle_printer_found = False
                for printer_name, printer_attributes in printers.items():
                    if (
                        "printer-state" in printer_attributes
                        and printer_attributes["printer-state"] == 3
                    ):
                        idle_printer_found = True
                        break
                self.printer_state = idle_printer_found

            self.status_updated.emit(self.printer_state)
        except Exception as e:
            print(e)
            self.status_updated.emit(False)

    def stop(self):
        self.running = False


class CheckPrinterStatusWindow(QDialog):
    printer_status_updated = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 900)
        self.setStyleSheet("background-color: #EBEBEB;")
        self.setup_ui()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        self.printer_status_thread = PrinterStatus()
        self.printer_status_thread.status_updated.connect(self.update_status)
        self.printer_status_thread.start()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        upper_layout = QHBoxLayout()
        upper_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        upper_layout.setSpacing(167)

        self.close_button = QPushButton()
        self.close_button.setFocusPolicy(Qt.NoFocus)
        self.close_button.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/static/close_img.png');}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/static/close_img_pressed.png');}"
        )
        self.close_button.setFixedSize(45, 45)
        self.close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.close_button.clicked.connect(self.close_window)

        self.help_label = QLabel("Printer Status")
        self.help_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 22px;
            color: #19323C;
            """
        )

        status_layout = QVBoxLayout()

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("margin-left: 18px; margin-top: 95px;")
        self.movie = QMovie("./img/animated_printer.gif")
        self.gif_label.setMovie(self.movie)
        self.movie.start()

        self.status_label = QLabel()
        self.status_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 38px;
            """
        )
        self.status_label.setAlignment(Qt.AlignCenter)

        self.status_checker_label = QLabel("Checking Printer Status.")
        self.status_checker_label.setStyleSheet(
            """
            font-family: Open Sans;
            font-size: 16px;
            margin-bottom: 180px;
            """
        )
        self.status_checker_label.setAlignment(Qt.AlignCenter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_label)
        self.timer.start(500)

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_checker_label)

        upper_layout.addWidget(self.close_button, Qt.AlignLeft)
        upper_layout.addWidget(self.help_label)
        upper_layout.setContentsMargins(8, 15, 0, 0)

        self.layout.addLayout(upper_layout)
        self.layout.addWidget(self.gif_label)
        self.layout.addLayout(status_layout)

    @pyqtSlot(bool)
    def update_status(self, is_available):
        self.is_available = is_available

        if self.is_available:
            self.status_label.setText("Printer is Available")
        else:
            self.status_label.setText("Printer is Offline")

    def update_label(self):
        text = self.status_checker_label.text()
        if text.endswith("...."):
            text = text[:-4]
        else:
            text += "."
        self.status_checker_label.setText(text)

    def close_window(self):
        self.close()
        self.printer_status_thread.stop()
        self.printer_status_thread.wait()
        self.printer_status_updated.emit(self.is_available)


class RefillButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        pixmap = QPixmap("./img/static/ink_level_img.png")
        scaled_pixmap = pixmap.scaled(
            65, 65, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label = QLabel()
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("margin-top: 15px;")

        self.label = QLabel("Refill Ink")
        self.label.setStyleSheet(
            """
            font-family: Roboto; 
            font-size: 14px;
            font-weight: bold;
            color: #19323C;
            """
        )

        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setFocusPolicy(Qt.NoFocus)
        self.setLayout(layout)


class ChangePasswordButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()

        pixmap = QPixmap("./img/static/password_img.png")
        scaled_pixmap = pixmap.scaled(
            65, 65, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label = QLabel()
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("margin-top: 15px;")

        self.label = QLabel("Change Password")
        self.label.setWordWrap(True)
        self.label.setStyleSheet(
            """
            font-family: Roboto; 
            font-size: 14px;
            font-weight: bold;
            color: #19323C;
            """
        )

        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setFocusPolicy(Qt.NoFocus)
        self.setLayout(layout)


class ChangePasswordWindow(QDialog):
    close_message_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(600, 900)
        self.setStyleSheet("background-color: #EBEBEB;")
        self.setup_ui()

        # Connect database
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT admin_password FROM kiosk_settings LIMIT 1")
        self.admin_password = cursor.fetchone()[0]

        conn.close()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        upper_layout = QHBoxLayout()
        upper_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        upper_layout.setSpacing(157)

        self.close_button = QPushButton()
        self.close_button.setFocusPolicy(Qt.NoFocus)
        self.close_button.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/static/close_img.png');}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/static/close_img_pressed.png');}"
        )
        self.close_button.setFixedSize(45, 45)
        self.close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.close_button.clicked.connect(lambda: self.close())

        self.help_label = QLabel("Change Password")
        self.help_label.setStyleSheet(
            """
            font-family: Montserrat;
            font-size: 22px;
            color: #19323C;
            """
        )

        upper_layout.addWidget(self.close_button, Qt.AlignLeft)
        upper_layout.addWidget(self.help_label)
        upper_layout.setContentsMargins(8, 15, 0, 0)

        self.input_edit = QLineEdit()
        self.input_edit.setFixedWidth(480)
        self.input_edit.setAlignment(Qt.AlignCenter)
        self.input_edit.setEchoMode(QLineEdit.Password)
        self.input_edit.setMaxLength(4)
        self.input_edit.setStyleSheet(
            """
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;  /* Dark gray color */
                border-radius: 10px;
                border: 3px solid #7C2F3E;  /* Light gray border */
                padding: 10px 20px;
                font-size: 48px;
                margin-top: 65px;
            }
            """
        )

        self.keypad_layout = QGridLayout()
        self.create_number_buttons()

        # Login button
        self.change_button = QPushButton("Change")
        self.change_button.setFocusPolicy(Qt.NoFocus)
        self.change_button.clicked.connect(self.on_change_click)

        # Apply minimalist style to buttons
        self.apply_minimalist_style(self.change_button)

        # Add input field and login button to the keypad layout
        self.keypad_layout.addWidget(self.input_edit, 0, 0, 1, 3)
        self.keypad_layout.addWidget(self.change_button, 5, 1)
        self.keypad_layout.setContentsMargins(0, 0, 0, 150)

        self.layout.addLayout(upper_layout)
        self.layout.addWidget(self.input_edit, alignment=Qt.AlignCenter)
        self.layout.addLayout(self.keypad_layout)

    def create_number_buttons(self):
        numbers = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "Clear",
            "0",
            "Backspace",
        ]

        positions = [(i, j) for i in range(4) for j in range(3)]

        for position, number in zip(positions, numbers):
            row, col = position
            button = QPushButton(number)
            button.setFocusPolicy(Qt.NoFocus)
            button.clicked.connect(self.on_button_click)
            self.keypad_layout.addWidget(button, row + 1, col)
            self.apply_minimalist_style(button)

    def apply_minimalist_style(self, button):
        button.setStyleSheet(
            "QPushButton {"
            "background-color: #7C2F3E;"  # Blue color
            "color: #FFFFFF;"  # White text color
            "border-radius: 10px;"
            "padding: 20px 40px;"
            "font-size: 24px;"
            "}"
            "QPushButton:pressed {"
            "background-color: #D8973C;"  # Even darker blue color when pressed
            "}"
        )

    def on_button_click(self):
        clicked_button = self.sender()
        clicked_text = clicked_button.text()

        if clicked_text == "Clear":
            self.input_edit.clear()
        elif clicked_text == "Backspace":
            current_text = self.input_edit.text()
            self.input_edit.setText(current_text[:-1])
        else:
            current_text = self.input_edit.text()
            self.input_edit.setText(current_text + clicked_text)

    def on_change_click(self):
        input_password = self.input_edit.text()

        try:
            conn = sqlite3.connect("./database/kiosk.db")
            cursor = conn.cursor()

            cursor.execute("BEGIN TRANSACTION")

            cursor.execute(
                """
                UPDATE kiosk_settings
                SET admin_password = ?
                WHERE ROWID = (
                    SELECT ROWID
                    FROM kiosk_settings
                    ORDER BY ROWID
                    LIMIT 1
                )
            """,
                (input_password,),
            )

            cursor.execute("COMMIT")

            # Display dialog box indicating success
            message_box = CustomMessageBox(
                "Success", "Password changed successfully.", parent=self
            )
            message_box.ok_button_clicked.connect(self.close_message)
            message_box.exec_()

        except sqlite3.Error as error:
            conn.rollback()
            print("Error changing price:", error)

        finally:
            if conn:
                conn.close()

    def close_message(self):
        self.input_edit.clear()


class AdminWindowWidget(QWidget):
    home_screen_backbt_clicked = pyqtSignal()
    bondpaper_quantity_updated = pyqtSignal(int)
    printer_updated = pyqtSignal(bool)

    def __init__(self, parent, is_printer_available):
        super().__init__(parent)

        # Define instance variables for temporary values
        self.id_num = 0
        self.form_name = " "

        # connect database
        conn = sqlite3.connect("./database/kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        self.coins_left = cursor.fetchone()[0]

        cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
        self.bondpaper_quantity = cursor.fetchone()[0]

        cursor.execute("SELECT ink_level FROM kiosk_settings LIMIT 1")
        self.ink_level = cursor.fetchone()[0]

        cursor.execute("SELECT base_price FROM kiosk_settings LIMIT 1")
        self.base_price = cursor.fetchone()[0]

        conn.close()

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

        self.setup_ui(is_printer_available)

        self.btn_1.clicked.connect(self.button1)
        self.btn_2.clicked.connect(self.button2)
        self.btn_3.clicked.connect(self.button3)
        self.btn_4.clicked.connect(self.button4)
        self.btn_5.clicked.connect(self.button5)

        self.active_button = self.btn_1
        self.update_button_styles()

    def setup_ui(self, is_printer_available):
        layout = QVBoxLayout(self)

        # Adding labels in top right corner
        rectangle_layout = QHBoxLayout()

        help_button = QPushButton()
        help_button.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/static/help_img.png');}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/static/help_img_pressed.png');}"
        )
        help_button.setFixedSize(65, 65)
        help_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        help_button.clicked.connect(self.show_help)

        rectangle_layout.addWidget(help_button, alignment=Qt.AlignRight)

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
        rectangle_layout.setContentsMargins(475, 25, 60, 0)

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
        self.bondpaper_label = QLabel(str(self.bondpaper_quantity))
        self.bondpaper_quantity_updated.connect(self.update_label_slot)
        bondpaper_layout.addWidget(self.bondpaper_warning)
        bondpaper_layout.addWidget(bondpaper_img)
        bondpaper_layout.addWidget(self.bondpaper_label, alignment=Qt.AlignLeft)

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
        self.printer_updated.connect(self.update_printer_status)
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

        self.left_layout = QVBoxLayout()
        self.sidebar_buttons = [
            self.btn_1,
            self.btn_2,
            self.btn_3,
            self.btn_4,
            self.btn_5,
        ]

        for button in self.sidebar_buttons:
            self.left_layout.addWidget(button)

        self.left_layout.addStretch(5)
        self.left_layout.setSpacing(20)

        system_layout = QVBoxLayout()

        system_bt = QPushButton()
        system_bt.setFocusPolicy(Qt.NoFocus)
        system_bt.setFixedSize(50, 50)
        system_bt.setStyleSheet(
            "QPushButton {background-color: transparent; border: none; image: url('img/static/system.png');}"
            "QPushButton:pressed {background-color: transparent; border: none; image: url('img/static/system_pressed.png');}"
        )
        system_bt.clicked.connect(self.show_system_button)

        frame = QFrame()

        frame_layout = QVBoxLayout()

        self.logout_bt = QPushButton("Logout")
        self.logout_bt.setFocusPolicy(Qt.NoFocus)
        self.logout_bt.setFixedHeight(70)
        self.logout_bt.setStyleSheet(
            """
            QPushButton {
                border: 2px solid #555555;
                background-color: #A9A9A9;
                border-radius: 15px;
                color: #19323C;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: Montserrat;
            }
            QPushButton::pressed {
                background-color: #555555;
                color: #FDFDFD;
            }
            """
        )
        self.logout_bt.clicked.connect(self.logout)
        self.logout_bt.hide()

        self.restart_bt = QPushButton("Restart")
        self.restart_bt.setFocusPolicy(Qt.NoFocus)
        self.restart_bt.setFixedHeight(70)
        self.restart_bt.setStyleSheet(
            """
            QPushButton {
                border: 2px solid #555555;
                background-color: #A9A9A9;
                border-radius: 15px;
                color: #19323C;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: Montserrat;
            }
            QPushButton::pressed {
                background-color: #555555;
                color: #FDFDFD;
            }
            """
        )
        self.restart_bt.clicked.connect(self.restart_app)
        self.restart_bt.hide()

        self.shutdown_bt = QPushButton("Shutdown")
        self.shutdown_bt.setFocusPolicy(Qt.NoFocus)
        self.shutdown_bt.setFixedHeight(70)
        self.shutdown_bt.setStyleSheet(
            """
            QPushButton {
                border: 2px solid #555555;
                background-color: #A9A9A9;
                border-radius: 15px;
                color: #19323C;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: Montserrat;
            }
            QPushButton::pressed {
                background-color: #555555;
                color: #FDFDFD;
            }
            """
        )
        self.shutdown_bt.clicked.connect(self.shutdown_app)
        self.shutdown_bt.hide()

        self.buttons_visible = False

        frame_layout.addWidget(self.logout_bt)
        frame_layout.addWidget(self.restart_bt)
        frame_layout.addWidget(self.shutdown_bt)
        frame_layout.setSpacing(10)
        frame_layout.setContentsMargins(15, 0, 0, 0)
        frame.setLayout(frame_layout)

        system_layout.addWidget(frame, alignment=Qt.AlignTop)
        system_layout.addWidget(system_bt, alignment=Qt.AlignRight)
        system_layout.setContentsMargins(0, 0, 0, 60)

        self.left_layout.addLayout(system_layout)

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
        shadow_effect1 = QGraphicsDropShadowEffect()
        shadow_effect1.setBlurRadius(50)
        shadow_effect1.setColor(Qt.gray)
        shadow_effect1.setOffset(0, 0)  # Adjust the shadow's offset as needed

        shadow_effect2 = QGraphicsDropShadowEffect()
        shadow_effect2.setBlurRadius(50)
        shadow_effect2.setColor(Qt.gray)
        shadow_effect2.setOffset(0, 0)  # Adjust the shadow's offset as needed

        # Create a vertical layout to center the frames vertically
        center_layout = QVBoxLayout()
        center_layout.addStretch(1)  # Add stretch to center vertically

        frames_layout = QHBoxLayout()
        frames_layout.setSpacing(45)

        # Create the first frame
        frame1 = QFrame()
        frame1.setFixedSize(500, 680)
        frame1.setStyleSheet(
            """
            background-color: #FFFFFF;
            border-radius: 25px;
            """
        )
        frame1.setGraphicsEffect(shadow_effect1)
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
        bondpaper_decrement_button.setFocusPolicy(Qt.NoFocus)
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
        refill_button.setFocusPolicy(Qt.NoFocus)
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
        bondpaper_increment_button.setFocusPolicy(Qt.NoFocus)
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

        button_center_layout = QVBoxLayout()

        ink_refill = RefillButton()
        ink_refill.setStyleSheet(
            """
            QPushButton {
                border-radius: 25px;
                background-color: #D8C995;
            }
            QPushButton::pressed {
                background-color: #FDFDFD;
            }
            """
        )
        ink_refill.setFixedSize(150, 150)
        ink_refill.clicked.connect(self.refill_ink)
        button_center_layout.addWidget(ink_refill)

        change_password_button = ChangePasswordButton()
        change_password_button.setStyleSheet(
            """
            QPushButton {
                border-radius: 25px;
                background-color: #D8C995;
            }
            QPushButton::pressed {
                background-color: #FDFDFD;
            }
            """
        )
        change_password_button.setFixedSize(150, 150)
        change_password_button.clicked.connect(self.change_password)
        button_center_layout.addWidget(change_password_button)

        frames_layout.addLayout(button_center_layout)

        # Create the second frame
        frame2 = QFrame()
        frame2.setFixedSize(500, 680)
        frame2.setStyleSheet(
            """
            background-color: #FFFFFF;
            border-radius: 25px;
            """
        )
        frame2.setGraphicsEffect(shadow_effect2)
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

        self.price_value = self.base_price
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
        price_decrement_button.setFocusPolicy(Qt.NoFocus)
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
        change_price_button.setFocusPolicy(Qt.NoFocus)
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
        price_increment_button.setFocusPolicy(Qt.NoFocus)
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
        bondpaper_amount = 100 - self.bondpaper_quantity
        if self.number_value < (bondpaper_amount // 10) * 10:
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
            connection = sqlite3.connect("./database/kiosk.db")
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
            message_box.ok_button_clicked.connect(self.re_init)
            message_box.exec_()

        except sqlite3.Error as error:
            connection.rollback()
            print("Error changing price:", error)

        finally:
            if connection:
                connection.close()

    def refill_bondpaper(self):
        bondpaper_quantity = self.number_value

        if (self.bondpaper_quantity + 10) > 100:
            # Display dialog box indicating success
            message_box = MessageBox(
                "Error",
                "You have exceeded the amount of bondpaper that can be stored in the printer.",
                parent=self,
            )
            message_box.exec_()
        else:
            try:
                with sqlite3.connect("./database/kiosk.db") as connection:
                    connection.execute("BEGIN TRANSACTION")

                    connection.execute(
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

                    connection.execute("COMMIT")

                    cursor = connection.execute(
                        "SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1"
                    )
                    self.bondpaper_quantity = cursor.fetchone()[0]

                    print(self.bondpaper_quantity)
                    print("Bondpaper refilled successfully.")

                    # Emit signal to update label
                    self.bondpaper_quantity_updated.emit(self.bondpaper_quantity)

                    # Display dialog box indicating success
                    message_box = CustomMessageBox(
                        "Success", "Bondpaper refilled successfully.", parent=self
                    )
                    message_box.ok_button_clicked.connect(self.re_init)
                    message_box.exec_()

            except sqlite3.Error as error:
                print("Error changing price:", error)

    def refill_ink(self):
        try:
            with sqlite3.connect("./database/kiosk.db") as connection:
                connection.execute("BEGIN TRANSACTION")

                connection.execute(
                    """
                    UPDATE kiosk_settings
                    SET ink_level = 1500
                    WHERE ROWID = (
                        SELECT ROWID
                        FROM kiosk_settings
                        ORDER BY ROWID
                        LIMIT 1
                    )
                    """
                )

                connection.execute("COMMIT")

                # Display dialog box indicating success
                message_box = CustomMessageBox(
                    "Success", "Ink refilled successfully.", parent=self
                )
                message_box.ok_button_clicked.connect(self.re_init)
                message_box.exec_()

        except sqlite3.Error as error:
            print("Error changing price:", error)

    def change_password(self):
        password_message_box = ChangePasswordWindow(self)
        parent_pos = self.mapToGlobal(self.rect().center())
        password_message_box.move(parent_pos - password_message_box.rect().center())
        password_message_box.exec_()

    # Slot to update the bondpaper label
    def update_label_slot(self, new_quantity):
        self.bondpaper_label.setText(str(new_quantity))

    def populate_table(self):
        try:
            connection = sqlite3.connect("./database/kiosk.db")
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM kiosk_print_results")
            data = cursor.fetchall()

            data.sort(reverse=True)

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
        conn = sqlite3.connect("./database/kiosk.db")
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
            conn = sqlite3.connect("./database/kiosk.db")
            cursor = conn.cursor()

            cursor.execute("DELETE FROM kiosk_forms WHERE id = ?", (index,))

            conn.commit()  # Commit changes to the database
            conn.close()

            delete_form_file(form_name)
            delete_process_file(form_name)
            delete_form_preview(form_name)

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

    def show_help(self):
        help_message_box = HelpMessageBox(self)
        parent_pos = self.mapToGlobal(self.rect().center())
        help_message_box.move(parent_pos - help_message_box.rect().center())
        help_message_box.exec_()

    def printer_not_connected(self):
        printer_status_window = CheckPrinterStatusWindow(self)
        parent_pos = self.mapToGlobal(self.rect().center())
        printer_status_window.move(parent_pos - printer_status_window.rect().center())
        printer_status_window.printer_status_updated.connect(self.send_printer_status)
        printer_status_window.exec_()

    @pyqtSlot(bool)
    def send_printer_status(self, is_available):
        self.printer_updated.emit(is_available)

    @pyqtSlot(bool)
    def update_printer_status(self, is_available):
        if is_available:
            self.printer_warning.hide()
            self.printer_status_symbol.setText("✓")
        else:
            self.printer_warning.show()
            self.printer_status_symbol.setText("✕")

    def low_bondpaper(self):
        self.delete_message_box = MessageBox(
            "Error",
            "Uh-oh, it seems the bond paper supply is low. Please refill immediately the bondpaper tray.",
            parent=self,
        )
        self.delete_message_box.exec_()

    def low_ink(self):
        self.delete_message_box = MessageBox(
            "Error",
            "Uh-oh, it seems the ink supply is low. Please refill immediately the ink tank.",
            parent=self,
        )
        self.delete_message_box.exec_()

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

        self.active_button = self.btn_1
        self.update_button_styles()

    def is_printer_available(self):
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()

            if not printers:
                self.printer_state = False
                raise Exception("No printers available.")

            idle_printer_found = False
            for printer_name, printer_attributes in printers.items():
                if (
                    "printer-state" in printer_attributes
                    and printer_attributes["printer-state"] == 3
                ):
                    idle_printer_found = True
                    self.printer_state = True
                    break

            if not idle_printer_found:
                self.printer_state = False
                raise Exception("No idle printer available")

        except Exception as e:
            print("Error during printing:", e)

    def update_print_status(self, status):
        if status:
            self.printer_status_symbol.setText("✓")
        else:
            self.printer_status_symbol.setText("✕")
            self.printer_warning.show()

    def logout(self):
        self.setVisible(False)
        self.home_screen_backbt_clicked.emit()

    def show_system_button(self):
        if self.buttons_visible:
            self.logout_bt.hide()
            self.restart_bt.hide()
            self.shutdown_bt.hide()
        else:
            self.logout_bt.show()
            self.restart_bt.show()
            self.shutdown_bt.show()

        self.buttons_visible = not self.buttons_visible

    def restart_app(self):
        QApplication.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def shutdown_app(self):
        QApplication.quit()
