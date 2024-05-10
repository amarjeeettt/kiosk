import sqlite3
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
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor
from custom_message_box import CustomMessageBox


class AdminWindowWidget(QWidget):
    home_screen_backbt_clicked = pyqtSignal()
    bondpaper_quantity_updated = pyqtSignal(int)
    def __init__(self, parent):
        super().__init__(parent)

        # add all widgets
        self.btn_1 = QPushButton("Dashboard", self)
        self.btn_2 = QPushButton("Add Forms", self)
        self.btn_3 = QPushButton("Edit Forms", self)
        self.btn_4 = QPushButton("Delete Forms", self)
        self.btn_5 = QPushButton("Settings", self)
        self.btn_6 = QPushButton("Logout", self)

        self.btn_1.clicked.connect(self.button1)
        self.btn_2.clicked.connect(self.button2)
        self.btn_3.clicked.connect(self.button3)
        self.btn_4.clicked.connect(self.button4)
        self.btn_5.clicked.connect(self.button5)
        self.btn_6.clicked.connect(self.logout)

        # add tabs
        self.tab1 = self.ui1()
        self.tab2 = self.ui2()
        self.tab3 = self.ui3()
        self.tab4 = self.ui4()
        self.tab5 = self.ui5()

        self.setup_ui()

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

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.btn_1)
        left_layout.addWidget(self.btn_2)
        left_layout.addWidget(self.btn_3)
        left_layout.addWidget(self.btn_4)
        left_layout.addWidget(self.btn_5)
        left_layout.addWidget(self.btn_6)
        left_layout.addStretch(5)
        left_layout.setSpacing(20)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
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
            """QTabBar::tab{width: 0; \
            height: 0; margin: 0; padding: 0; border: none;}"""
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
        self.right_widget.setCurrentIndex(0)

    def button2(self):
        self.right_widget.setCurrentIndex(1)

    def button3(self):
        self.right_widget.setCurrentIndex(2)

    def button4(self):
        self.right_widget.setCurrentIndex(3)

    def button5(self):
        self.right_widget.setCurrentIndex(4)

    # -----------------
    # pages

    def ui1(self):
        main_layout = QVBoxLayout()

        title_label = QLabel("Dashboard")
        main_layout.addWidget(title_label)

        # Add rectangle frame with labels
        rectangle_frame = QFrame()
        rectangle_frame.setFrameShape(QFrame.StyledPanel)
        rectangle_frame.setStyleSheet(
            "background-color: #FFFFFF; border: 2px solid #000000; border-radius: 5px;"
        )
        rectangle_layout = QHBoxLayout(rectangle_frame)

        label1 = QLabel("Label 1")
        label2 = QLabel("Label 2")
        label3 = QLabel("Label 3")

        rectangle_layout.addWidget(label1)

        # Create a QVBoxLayout for label2 and label3
        text_layout = QVBoxLayout()
        text_layout.addWidget(label2)
        text_layout.addWidget(label3)

        # Add text_layout to rectangle_layout
        rectangle_layout.addLayout(text_layout)

        # Set size policy of the rectangle frame
        rectangle_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        main_layout.addWidget(rectangle_frame)

        # Add second rectangle frame with labels
        rectangle_frame2 = QFrame()
        rectangle_frame2.setFrameShape(QFrame.StyledPanel)
        rectangle_frame2.setStyleSheet(
            "background-color: #FFFFFF; border: 2px solid #000000; border-radius: 5px;"
        )
        rectangle_layout2 = QHBoxLayout(rectangle_frame2)

        label4 = QLabel("Label 4")
        label5 = QLabel("Label 5")
        label6 = QLabel("Label 6")

        rectangle_layout2.addWidget(label4)

        # Create a QVBoxLayout for label5 and label6
        text_layout2 = QVBoxLayout()
        text_layout2.addWidget(label5)
        text_layout2.addWidget(label6)

        # Add text_layout2 to rectangle_layout2
        rectangle_layout2.addLayout(text_layout2)

        # Set size policy of the second rectangle frame
        rectangle_frame2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        main_layout.addWidget(rectangle_frame2)

        # Create a table
        self.tableWidget = QTableWidget()
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.tableWidget)
        main_layout.addLayout(table_layout)

        self.populate_table()

        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui2(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("page 2"))
        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui3(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("page 3"))
        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui4(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("page 4"))
        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui5(self):
        main_layout = QVBoxLayout()
        
        settings_label = QLabel("Settings")
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

        main_layout.addLayout(
            center_layout
        )
        main = QWidget()
        main.setLayout(main_layout)
        return main

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

    def logout(self):
        self.setVisible(False)
        self.home_screen_backbt_clicked.emit()