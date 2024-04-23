import sqlite3
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHeaderView,
    QHBoxLayout,
    QInputDialog,
    QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal


class AdminScreenWindow(QMainWindow):
    home_screen_backbt_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Database Table")
        self.showMaximized()
        
        # connect database
        conn = sqlite3.connect("kiosk.db")
        cursor = conn.cursor()

        cursor.execute("SELECT coins_left FROM kiosk_settings LIMIT 1")
        self.coins_left = cursor.fetchone()[0]

        cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
        self.bondpaper_quantity = cursor.fetchone()[0]

        conn.close()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        
        # Adding back button and labels in top right corner
        top_layout = QHBoxLayout()

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
        
        layout.addLayout(top_layout)

        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        button_below_table_container = QWidget()
        button_below_table_layout = QVBoxLayout(button_below_table_container)
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
                background-color: #A93F55;
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
        button_below_table_layout.addWidget(button1)
        button_below_table_layout.addWidget(button2)

        button1.clicked.connect(self.refill_bondpaper)
        button2.clicked.connect(self.change_price)

    def populate_table(self):
        try:
            connection = sqlite3.connect("kiosk.db")
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM kiosk_print_results")
            data = cursor.fetchall()

            column_names = [description[0] for description in cursor.description]

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

    def go_back(self):
        self.close()
        self.home_screen_backbt_clicked.emit()

    def refill_bondpaper(self):
        try:
            connection = sqlite3.connect("kiosk.db")
            cursor = connection.cursor()

            cursor.execute("BEGIN TRANSACTION")

            cursor.execute(
                """
                UPDATE kiosk_settings
                SET bondpaper_quantity = 45
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
