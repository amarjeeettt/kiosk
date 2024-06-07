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
    QTextBrowser,
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import (
    Qt,
    QTimer,
    QEvent,
    QPropertyAnimation,
    QEasingCurve,
    pyqtSignal,
)


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


class WarningMessageBox(QDialog):
    continue_bt_clicked = pyqtSignal()
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
            "font-size: 16px; font-family: Roboto; margin-left: 15px; margin-right: 15px"
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
        self.continue_bt_clicked.emit()
        self.accept()

    def return_clicked(self):
        self.return_bt_clicked.emit()
        self.close()


class HelpMessageButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()

        self.label = QLabel(title)
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

        button_layout.addWidget(self.label)
        button_layout.addWidget(self.image_label, alignment=Qt.AlignRight)

        layout.addLayout(button_layout)  # Add button_layout to the existing layout

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
    close_message_clicked = pyqtSignal()

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
        self.close_button.setFocusPolicy(Qt.NoFocus)
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
        self.back_button.setFocusPolicy(Qt.NoFocus)
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

        self.help_title_label = QLabel("User Printing and Viewing Forms Guide")
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

        button_layout = QVBoxLayout()

        self.how_to_print = HelpMessageButton("How to Print?", self)
        self.how_to_view = HelpMessageButton("How to View the Process?", self)
        self.how_to_add = HelpMessageButton("How to Add a Copy of the Form?", self)
        self.how_to_remove = HelpMessageButton(
            "How to Remove the Added Copy of the Form?", self
        )
        self.payment_method = HelpMessageButton("Payment Method?", self)
        self.extra_coin = HelpMessageButton(
            "Can I Get Back the Extra Coin I Inserted?", self
        )
        self.retrieve_coins = HelpMessageButton(
            "If the kiosk encounters a printing failure or system shutdown after I have inserted coins, can I retrieve my coins?",
            self,
        )
        self.student_request = HelpMessageButton(
            "Can Students Request Specific Forms?", self
        )

        self.how_to_print.clicked.connect(self.how_to_print_form)
        self.how_to_view.clicked.connect(self.how_to_view_form)
        self.how_to_add.clicked.connect(self.how_to_add_copy)
        self.how_to_remove.clicked.connect(self.how_to_remove_copy)
        self.payment_method.clicked.connect(self.payment)
        self.extra_coin.clicked.connect(self.get_back_coins)
        self.retrieve_coins.clicked.connect(self.retrieve_coins_inserted)
        self.student_request.clicked.connect(self.student_request_form)

        self.lines = []
        self.add_widget_with_line(button_layout, self.how_to_print)
        self.add_widget_with_line(button_layout, self.how_to_view)
        self.add_widget_with_line(button_layout, self.how_to_add)
        self.add_widget_with_line(button_layout, self.how_to_remove)
        self.add_widget_with_line(button_layout, self.payment_method)
        self.add_widget_with_line(button_layout, self.extra_coin)
        self.add_widget_with_line(button_layout, self.retrieve_coins)
        button_layout.addWidget(self.student_request)
        button_layout.setContentsMargins(0, 0, 0, 135)

        self.layout.addLayout(upper_layout)
        self.layout.addLayout(back_layout)
        self.layout.addWidget(self.help_title_label)
        self.layout.addWidget(self.help_text)
        self.layout.addLayout(button_layout)

    def how_to_print_form(self):
        self.hide_buttons(
            self.how_to_print,
            self.how_to_view,
            self.how_to_add,
            self.how_to_remove,
            self.payment_method,
            self.extra_coin,
            self.retrieve_coins,
            self.student_request,
        )

        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()

        self.help_title_label.setText("How to Print?")

        html_content = """
        <ol>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Access the Forms Dashboard</strong><br>
            First, go to the forms dashboard.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Find Your Needed Form</strong><br>
            Find your needed form by clicking its category button at the top of the dashboard or by scrolling through the list.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Click the “View” Button</strong><br>
            Select the form by clicking the “View” button to preview the form and start the printing process.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Adjust the Number of Copies</strong><br>
            You can adjust the number of copies by clicking the plus sign (+) icon to add more copies or the minus sign (-) icon to reduce the number of copies. Here, you will also see the total cost of the form and the number of copies.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Proceed with Payment</strong><br>
            Click the “Print Forms” button to proceed to the payment transaction. You can pay with both old and new types of coins.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Enable the Print Button</strong><br>
            If you pay the exact amount, the “Print” button will be enabled. Once you click the button, the printing will start. However, if your payment exceeds the exact amount, a warning message will pop up to hold the printing. The warning message 
            will notify you that you inserted an excess amount and that once you click the “Confirm” button, you cannot retrieve the excess amount. But if you click the “Cancel” button, you will have the chance to edit the number of copies of the form 
            cto consume all the coins you’ve inserted.</li><br>
        </ol>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def how_to_view_form(self):
        self.hide_buttons(
            self.how_to_print,
            self.how_to_view,
            self.how_to_add,
            self.how_to_remove,
            self.payment_method,
            self.extra_coin,
            self.retrieve_coins,
            self.student_request,
        )

        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()

        self.help_title_label.setText("How to View the Process?")

        html_content = """
        <ol>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Access the Forms Dashboard</strong><br>
            First, go to the forms dashboard.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Find Your Needed Form</strong><br>
            Find your needed form by clicking its category button at the top of the dashboard or by scrolling through the list.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Click the “View” Button</strong><br>
            Select the form by clicking the “View” button to preview the form and start the printing process.</li><br>
            <li style="font-size: 16px; margin-left: 8px;"><strong>Click the “View Process” Button</strong><br>
            Click the “View Process” button to view the step-by-step guidance process, map, and requirements of the forms.</li><br>
        </ol>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def how_to_add_copy(self):
        self.hide_buttons(
            self.how_to_print,
            self.how_to_view,
            self.how_to_add,
            self.how_to_remove,
            self.payment_method,
            self.extra_coin,
            self.retrieve_coins,
            self.student_request,
        )

        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()

        self.help_title_label.setText("How to Add a Copy of the Form?")

        html_content = """
            <li style="font-size: 16px; margin-left: 8px; margin-right: 30px;"><strong>Click the “Add Sign (+)” Button</strong><br>
            To add a copy of the form, click the plus sign (+) icon. By following this simple step, you can easily add additional copies
            of the form as needed.</li><br>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def how_to_remove_copy(self):
        self.hide_buttons(
            self.how_to_print,
            self.how_to_view,
            self.how_to_add,
            self.how_to_remove,
            self.payment_method,
            self.extra_coin,
            self.retrieve_coins,
            self.student_request,
        )

        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()

        self.help_title_label.setText("How to Remove the Added Copy of the Form?")

        html_content = """
            <li style="font-size: 16px; margin-left: 8px; margin-right: 30px;"><strong>Click the “Minus Sign (-)” Button</strong><br>
            To remove an added copy of the form, click the minus sign (-) icon. By following this simple step, you can easily reduce the number of copies of the form as needed.</li><br>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def payment(self):
        self.hide_buttons(
            self.how_to_print,
            self.how_to_view,
            self.how_to_add,
            self.how_to_remove,
            self.payment_method,
            self.extra_coin,
            self.retrieve_coins,
            self.student_request,
        )

        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()

        self.help_title_label.setText("Payment Method?")

        html_content = """
            <li style="font-size: 16px; margin-left: 8px; margin-right: 30px;">Our system accepts payment exclusively in peso coins. 
            This means that students must use peso coins to pay for the forms they wish to print. <strong>No change provided</strong>, 
            our system does not offer change. If you insert more coins than required , the excess amount will not be refunded. If you 
            overpay, you will have the option to adjust the number of copies to consume the extra amount.</li><br>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def get_back_coins(self):
        self.hide_buttons(
            self.how_to_print,
            self.how_to_view,
            self.how_to_add,
            self.how_to_remove,
            self.payment_method,
            self.extra_coin,
            self.retrieve_coins,
            self.student_request,
        )

        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()

        self.help_title_label.setText("Can I Get Back the Extra Coin I Inserted?")

        html_content = """
            <li style="font-size: 16px; margin-left: 8px; margin-right: 30px;"><strong>Unfortunately, if you insert an extra coin, you cannot get it back.</strong> 
            Once you click the “Confirm” button after inserting the coins, the excess amount cannot be refunded. However, if you click the “Cancel” button, you will 
            have the chance to edit the number of copies of the form to utilize the extra amount you have inserted.</li><br>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def retrieve_coins_inserted(self):
        self.hide_buttons(
            self.how_to_print,
            self.how_to_view,
            self.how_to_add,
            self.how_to_remove,
            self.payment_method,
            self.extra_coin,
            self.retrieve_coins,
            self.student_request,
        )

        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()

        self.help_title_label.setText(
            "If the kiosk encounters a printing failure or system shutdown after I have inserted coins, can I retrieve my coins?"
        )

        html_content = """
            <p style="font-size: 16px; margin-left: 8px;"><strong>Regarding the issue of whether you can retrieve coins inserted into the Pay-Per-Print kiosk when there is a printing failure, system shutdown, or other system errors, the answer is no, you cannot directly retrieve the coins.</strong>
                However, the system does ensure that the value of the coins you've inserted is stored and can still be utilized. This means that even if there is a temporary disruption or failure, the amount you've paid is not lost.</p>
            <ol>
                <li style="font-size: 16px; margin-left: 8px;"><strong>Coin Insertion and Payment Capture</strong><br>
                When you insert coins into the Pay-Per-Print kiosk, the system captures and stores the value of the amount paid, even if an error occurs immediately after.</li><br>
                <li style="font-size: 16px; margin-left: 8px;"><strong>Error Handling</strong><br>
                If there's an error like a shutdown or printing failure, the system retains the record of the amount paid.</li><br>
                <li style="font-size: 16px; margin-left: 8px;"><strong>Utilizing Your Payment</strong><br>
                You can use the stored value to print other forms once the system is back online or the error is resolved. This means the money you put into the machine is not lost; it remains credited to your session or account until you use it for printing.</li><br>
                <li style="font-size: 16px; margin-left: 8px;"><strong>No Refunds</strong><br>
                It’s important to note that the kiosk does not refund any coins inserted. This is likely a design choice to simplify the mechanics and security of the kiosk.</li><br>
                <li style="font-size: 16px; margin-left: 8px;"><strong>Adjustments</strong><br>
                If you overpay due to the system not providing change, you have the option to adjust the number of copies to match the amount you've inserted, effectively using up the balance.</li><br>
            </ol>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def student_request_form(self):
        self.hide_buttons(
            self.how_to_print,
            self.how_to_view,
            self.how_to_add,
            self.how_to_remove,
            self.payment_method,
            self.extra_coin,
            self.retrieve_coins,
            self.student_request,
        )

        self.close_button.hide()
        self.help_label.hide()

        self.back_button.show()

        self.help_title_label.setText("Can Students Request Specific Forms?")

        html_content = """
            <li style="font-size: 16px; margin-left: 8px; margin-right: 30px;">No, students cannot request specific forms. They can only choose from the forms that are pre-set and provided by our system.</li><br>
        """
        self.help_text.setHtml(html_content)
        self.help_text.show()

    def go_back(self):
        self.show_buttons(
            self.how_to_print,
            self.how_to_view,
            self.how_to_add,
            self.how_to_remove,
            self.payment_method,
            self.extra_coin,
            self.retrieve_coins,
            self.student_request,
        )

        self.close_button.show()
        self.help_label.show()

        self.back_button.hide()

        self.help_title_label.setText("User Printing and Viewing Forms Guide")
        self.help_text.hide()

    def hide_buttons(self, *buttons):
        for button in buttons:
            button.hide()
        for line in self.lines:
            line.hide()

    def show_buttons(self, *buttons):
        for button in buttons:
            button.show()
        for line in self.lines:
            line.show()

    def add_widget_with_line(self, layout, widget):
        layout.addWidget(widget)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("QFrame { border: none; border-bottom: 1px solid #9D9D9D; }")
        layout.addWidget(line)
        self.lines.append(line)  # Store a reference to the line

    def close_message_box(self):
        self.close()
        self.close_message_clicked.emit()


class ButtonWidget(QWidget):
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
            font-size: 13px;
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
    view_process_button_clicked = pyqtSignal(str)
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
        self.nav_btn_category8.clicked.connect(self.filter_buttons_category8)

        # Set the active button initially
        self.active_button = self.nav_btn_all
        self.update_button_styles()

        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.setInterval(15000)
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
            self.printer_status_symbol.setText("✕")

        if self.bondpaper_quantity <= 5:
            self.bondpaper_warning.show()

        if self.ink_level <= 75:
            self.ink_warning.show()

        if not is_printer_available:
            self.printer_warning.show()
            self.printer_status_symbol.setText("✕")

        self.nav_btn_all = QPushButton("All")
        self.nav_btn_all.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category1 = QPushButton("Accreditation")
        self.nav_btn_category1.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category2 = QPushButton("Clearance")
        self.nav_btn_category2.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category3 = QPushButton("Enrollment")
        self.nav_btn_category3.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category4 = QPushButton("Graduation")
        self.nav_btn_category4.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category5 = QPushButton("Petition")
        self.nav_btn_category5.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category6 = QPushButton("Research")
        self.nav_btn_category6.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category7 = QPushButton("Controlled Forms")
        self.nav_btn_category7.setFocusPolicy(Qt.NoFocus)
        self.nav_btn_category8 = QPushButton("Others")
        self.nav_btn_category8.setFocusPolicy(Qt.NoFocus)

        # Set size policy for navigation buttons to Fixed
        self.nav_btn_all.setFixedSize(140, 65)
        self.nav_btn_all.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category1.setFixedHeight(65)
        self.nav_btn_category1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category2.setFixedHeight(65)
        self.nav_btn_category2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category3.setFixedHeight(65)
        self.nav_btn_category3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category4.setFixedHeight(65)
        self.nav_btn_category4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category5.setFixedHeight(65)
        self.nav_btn_category5.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category6.setFixedHeight(65)
        self.nav_btn_category6.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category7.setFixedHeight(65)
        self.nav_btn_category7.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.nav_btn_category8.setFixedHeight(65)
        self.nav_btn_category8.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

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
            self.nav_btn_category8,
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
                padding-bottom: 10px; 
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
        self.nav_btn_category8.setStyleSheet(nav_css)

        # Align the navigation bar to the top
        self.nav_layout.setAlignment(Qt.AlignTop)
        self.nav_layout.setSpacing(50)
        self.nav_layout.setContentsMargins(100, 20, 0, 0)

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
                padding-bottom: 10px; 
            }
        """
        )

    def filter_buttons_all(self):
        self.active_button = self.nav_btn_all
        self.filter_buttons(None)  # Pass None to show all buttons
        self.update_button_styles()
        self.reset_inactivity_timer()

    def filter_buttons_category1(self):
        self.active_button = self.nav_btn_category1
        self.filter_buttons("Accreditation")  # Filter by category
        self.update_button_styles()
        self.reset_inactivity_timer()

    def filter_buttons_category2(self):
        self.active_button = self.nav_btn_category2
        self.filter_buttons("Clearance")  # Filter by category
        self.update_button_styles()
        self.reset_inactivity_timer()

    def filter_buttons_category3(self):
        self.active_button = self.nav_btn_category3
        self.filter_buttons("Enrollment")  # Filter by category
        self.update_button_styles()
        self.reset_inactivity_timer()

    def filter_buttons_category4(self):
        self.active_button = self.nav_btn_category4
        self.filter_buttons("Graduation")  # Filter by category
        self.update_button_styles()
        self.reset_inactivity_timer()

    def filter_buttons_category5(self):
        self.active_button = self.nav_btn_category5
        self.filter_buttons("Petition")  # Filter by category
        self.update_button_styles()
        self.reset_inactivity_timer()

    def filter_buttons_category6(self):
        self.active_button = self.nav_btn_category6
        self.filter_buttons("Research")  # Filter by category
        self.update_button_styles()
        self.reset_inactivity_timer()

    def filter_buttons_category7(self):
        self.active_button = self.nav_btn_category7
        self.filter_buttons("Controlled Forms")  # Filter by category
        self.update_button_styles()
        self.reset_inactivity_timer()

    def filter_buttons_category8(self):
        self.active_button = self.nav_btn_category8
        self.filter_buttons("Other")  # Filter by category
        self.update_button_styles()
        self.reset_inactivity_timer()

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
        self.inactivity_timer.stop()
        controlled_form = [
            "Completion Form for Incomplete Grades",
            "Removal Form",
            "Dropping Form",
        ]

        if title in controlled_form:
            self.view_process_button_clicked.emit(title)
        else:
            self.view_button_clicked.emit(
                title,
                int(page_number),
                self.is_printer_available,
                self.bondpaper_supply,
                self.ink_supply,
            )

    def show_help(self):
        self.inactivity_timer.stop()
        help_message_box = HelpMessageBox(self)
        parent_pos = self.mapToGlobal(self.rect().center())
        help_message_box.move(parent_pos - help_message_box.rect().center())
        help_message_box.close_message_clicked.connect(self.reset_inactivity_timer)
        help_message_box.exec_()

    def printer_not_connected(self):
        self.inactivity_timer.stop()
        self.printer_message_box = WarningMessageBox(
            "Uh-oh, it seems the printer is currently offline or not available. Please contact the admin staff for further assistance.\n\n\nWould you like to proceed or return to the menu?",
            parent=self,
        )
        self.printer_message_box.continue_bt_clicked.connect(
            self.reset_inactivity_timer
        )
        self.printer_message_box.return_bt_clicked.connect(self.go_back)
        self.printer_message_box.exec_()

    def low_bondpaper(self):
        self.inactivity_timer.stop()
        self.bondpaper_message_box = WarningMessageBox(
            "Uh-oh, it seems the bondpaper supply is low. Please contact the admin staff for further assistance.\n\n\nWould you like to proceed or return to the menu?",
            parent=self,
        )
        self.bondpaper_message_box.continue_bt_clicked.connect(
            self.reset_inactivity_timer
        )
        self.bondpaper_message_box.return_bt_clicked.connect(self.go_back)
        self.bondpaper_message_box.exec_()

    def low_ink(self):
        self.inactivity_timer.stop()
        self.ink_message_box = WarningMessageBox(
            "Uh-oh, it seems the ink supply is low. Please contact the admin staff for further assistance.\n\n\nWould you like to proceed or return to the menu?",
            parent=self,
        )
        self.ink_message_box.continue_bt_clicked.connect(self.reset_inactivity_timer)
        self.ink_message_box.return_bt_clicked.connect(self.go_back)
        self.ink_message_box.exec_()

    def eventFilter(self, obj, event):
        if event.type() in [QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.KeyPress]:
            self.reset_inactivity_timer()
        return super(ViewFormWidget, self).eventFilter(obj, event)

    def reset_inactivity_timer(self):
        if self.inactivity_timer.isActive():
            self.inactivity_timer.stop()
        self.inactivity_timer.start()

    def go_back(self):
        self.inactivity_timer.stop()
        self.setVisible(False)
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
