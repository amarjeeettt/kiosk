from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QSize
import sqlite3

class AdminScreenWindow(QMainWindow):
    # Define a signal for back button clicked
    home_screen_backbt_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        # Set window size
        self.showMaximized()

        # Create a central widget for the window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a label to display some text in the window
        label = QLabel("This is the new window for admin view.")
        label.setAlignment(Qt.AlignCenter)  # Align text to the center
        
        self.back_bt = QPushButton("Back", self)
        self.back_bt.setStyleSheet(
            """
            QPushButton {
                background-color: #A93F55; 
                color: #F3F7F0; 
                font-family: Montserrat;
                font-size: 24px; 
                font-weight: bold; 
                letter-spacing: 3px;
                border-top-right-radius: 40px;
                border-bottom-right-radius: 40px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border: none;
                padding-right: 15px;
            }
            QPushButton:pressed {
                color: #D8C995;
            }
            """
        )
        self.back_bt.setFocusPolicy(Qt.NoFocus)
        self.back_bt.clicked.connect(self.go_back)
        
        # Create a layout for the button
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        # Add stretch to center the button vertically
        button_layout.addStretch()
        
        # Create the button
        self.execute_button = QPushButton("Execute SQL", self)
        self.execute_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.execute_button.clicked.connect(self.execute_sql)
        
        # Add the button to the layout
        button_layout.addWidget(self.execute_button)
        
        # Add stretch to center the button horizontally
        button_layout.addStretch()
        
        layout.addWidget(label)
        layout.addWidget(self.back_bt)
    
    # Slot to handle going back to the main window
    def go_back(self):
        self.close()
        self.home_screen_backbt_clicked.emit()
        
    # Slot to execute SQLite3 script and print result
    def execute_sql(self):
        try:
            connection = sqlite3.connect('kiosk.db')
            cursor = connection.cursor()

            # Your SQL script
            sql_script = """
            UPDATE kiosk_settings
            SET bondpaper_quantity = 5
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
