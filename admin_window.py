from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHeaderView, QHBoxLayout, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal
import sqlite3

class AdminScreenWindow(QMainWindow):
    home_screen_backbt_clicked = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Database Table")
        self.showMaximized()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Create a horizontal layout for the button above the table
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
        layout.addLayout(back_button_layout)

        # Create a table widget
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        # Create a widget to hold the buttons below the table
        button_below_table_container = QWidget()
        button_below_table_layout = QVBoxLayout(button_below_table_container)
        layout.addWidget(button_below_table_container)

        # Fetch data from database and populate table
        self.populate_table()
        
        # Set modern styling for the table
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

        # Create buttons below the table
        button1 = QPushButton("Refill Bondpaper")
        button2 = QPushButton("Change Price")
        button_below_table_layout.addWidget(button1)
        button_below_table_layout.addWidget(button2)

        # Connect button clicks to slots
        button1.clicked.connect(self.refill_bondpaper)
        button2.clicked.connect(self.change_price)

    def populate_table(self):
        # Connect to SQLite database
        connection = sqlite3.connect('kiosk.db')
        cursor = connection.cursor()

        # Fetch data from the database
        cursor.execute('''SELECT * FROM kiosk_print_results''')
        data = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]

        # Populate table with column names
        self.tableWidget.setColumnCount(len(column_names))
        self.tableWidget.setHorizontalHeaderLabels(column_names)

        # Populate table with data
        self.tableWidget.setRowCount(len(data))
        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.tableWidget.setItem(row_num, col_num, item)

        # Set resizing mode for columns to stretch
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Close database connection
        connection.close()

    def go_back(self):
        self.close()
        self.home_screen_backbt_clicked.emit()

    def refill_bondpaper(self):
        try:
            connection = sqlite3.connect('kiosk.db')
            cursor = connection.cursor()

            # Your SQL script
            sql_script = """
            UPDATE kiosk_settings
            SET bondpaper_quantity = 45
            WHERE ROWID = (
                SELECT ROWID
                FROM kiosk_settings
                ORDER BY ROWID
                LIMIT 1
            );
            """
            
            cursor.execute(sql_script)
            connection.commit()
            
            cursor.execute("SELECT bondpaper_quantity FROM kiosk_settings LIMIT 1")
            self.bondpaper_quantity = cursor.fetchone()[0]
            
            print(self.bondpaper_quantity)
            print("SQL script executed successfully.")

        except sqlite3.Error as error:
            print("Error executing SQL script:", error)

        finally:
            if connection:
                connection.close()

    def change_price(self):
        # Create an input dialog to get the new price from the user
        new_price, ok = QInputDialog.getDouble(self, "Change Price", "Enter the new price:")
        if ok:
            print("New Price:", new_price)
            try:
                connection = sqlite3.connect('kiosk.db')
                cursor = connection.cursor()

                # Your SQL script
                sql_script = """
                UPDATE kiosk_settings
                SET base_price = ?
                WHERE ROWID = (
                    SELECT ROWID
                    FROM kiosk_settings
                    ORDER BY ROWID
                    LIMIT 1
                );
                """
                
                cursor.execute(sql_script, (new_price,))
                connection.commit()
                
                cursor.execute("SELECT base_price FROM kiosk_settings LIMIT 1")
                self.base_price = cursor.fetchone()[0]
                
                print(self.base_price)
                print("SQL script executed successfully.")

            except sqlite3.Error as error:
                print("Error executing SQL script:", error)

            finally:
                if connection:
                    connection.close()