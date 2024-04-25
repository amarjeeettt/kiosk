import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHeaderView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QDesktopWidget,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from custom_message_box import CustomMessageBox


class AdminScreenWindow(QMainWindow):
    home_screen_backbt_clicked = pyqtSignal()

    # Define a signal for bondpaper quantity update
    bondpaper_quantity_updated = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        # Connect database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        self.coins_left = cursor.fetchone()[0]

        cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
        self.bondpaper_quantity = cursor.fetchone()[0]

        conn.close()

        self.set_background_image()
        self.showMaximized()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 35, 0, 0)

        # Adding back button and labels in top right corner
        top_layout = QHBoxLayout()

        # Add back button to the layout
        back_button_layout = QHBoxLayout()
        self.logout_bt = QPushButton("Logout")
        self.logout_bt.setStyleSheet(
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
        self.logout_bt.setFocusPolicy(Qt.NoFocus)
        self.logout_bt.clicked.connect(self.go_back)
        back_button_layout.addWidget(self.logout_bt, alignment=Qt.AlignLeft)
        top_layout.addLayout(back_button_layout)

        # Adding labels in top right corner
        top_right_layout = QHBoxLayout()
        self.label1 = QLabel(f"Bondpaper Left: {self.bondpaper_quantity}")
        label2 = QLabel(f"Coins Left: {self.coins_left}")
        top_right_layout.addWidget(self.label1, alignment=Qt.AlignRight)
        top_right_layout.addWidget(label2, alignment=Qt.AlignRight)
        top_right_layout.setSpacing(0)
        top_right_layout.setContentsMargins(0, 0, 130, 0)
        top_layout.addLayout(top_right_layout)

        layout.addLayout(top_layout)

        # Add vertical spacer between top_layout and tableWidget
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        )

        # Adjust the layout of the table widget to include margins on both sides
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(35, 0, 35, 0)

        self.tableWidget = QTableWidget()
        table_layout.addWidget(self.tableWidget)
        layout.addLayout(table_layout)

        button_below_table_container = QWidget()
        button_below_table_layout = QHBoxLayout(button_below_table_container)
        layout.addWidget(button_below_table_container)

        self.populate_table()

        self.tableWidget.setStyleSheet(
            """
            QTableWidget {
                background-color: #F3F7F0;
                color: #404040;
                font-family: Montserrat;
                font-size: 14px;
                border: 1px solid #D8C995;
            }
            QHeaderView::section {
                background-color: #7C2F3E;
                color: #F3F7F0;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
                border: none;
            }
            """
        )

        button1 = QPushButton("Refill Bondpaper")
        button2 = QPushButton("Change Price")

        button1.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                font-family: Montserrat;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                border: none;
                padding: 10px 20px;
                margin-right: 20px;
            }
            QPushButton:pressed {
                color: #dcdde1;
            }
            """
        )

        button2.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                font-family: Montserrat;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                border: none;
                padding: 10px 20px;
            }
            QPushButton:pressed {
                color: #dcdde1;
            }
            """
        )

        button_below_table_layout.addStretch(1)
        button_below_table_layout.addWidget(button1)
        button_below_table_layout.addWidget(button2)

        button1.clicked.connect(self.refill_bondpaper)
        button2.clicked.connect(self.change_price)

        # Add empty space below the buttons
        spacer = QSpacerItem(40, 60, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer)

        # Connect bondpaper_quantity_updated signal to update_label_slot
        self.bondpaper_quantity_updated.connect(self.update_label_slot)

    # Update the populate_table method
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

    def go_back(self):
        self.setVisible(False)
        self.home_screen_backbt_clicked.emit()

    def refill_bondpaper(self):
        try:
            connection = sqlite3.connect("kiosk.db")
            cursor = connection.cursor()

            cursor.execute("BEGIN TRANSACTION")

            cursor.execute(
                """
                UPDATE kiosk_settings
                SET bondpaper_quantity = 100
                WHERE ROWID = (
                    SELECT ROWID
                    FROM kiosk_settings
                    ORDER BY ROWID
                    LIMIT 1
                )
            """
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
            print("Error refilling bondpaper:", error)

        finally:
            if connection:
                connection.close()

    def change_price(self):
        new_price, ok = QInputDialog.getDouble(
            self, "Change Price", "Enter the new price:"
        )
        if ok:
            print("New Price:", new_price)
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

            except sqlite3.Error as error:
                connection.rollback()
                print("Error changing price:", error)

            finally:
                if connection:
                    connection.close()

    # Slot to update the bondpaper label
    def update_label_slot(self, new_quantity):
        self.label1.setText(f"Bondpaper Left: {new_quantity}")

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
