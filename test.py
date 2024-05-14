import sys
from PyQt5.QtWidgets import *

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # set the title of main window
        self.setWindowTitle('Sidebar layout - www.luochang.ink')

        # set the size of window
        self.Width = 800
        self.height = int(0.618 * self.Width)
        self.resize(self.Width, self.height)

        # Define instance variables for temporary values
        self.temp_value1 = 0
        self.temp_value2 = 0
        self.temp_value3 = ' '

        # add all widgets
        self.btn_1 = QPushButton('1', self)
        self.btn_2 = QPushButton('2', self)
        self.btn_3 = QPushButton('3', self)
        self.btn_4 = QPushButton('4', self)

        self.btn_1.setObjectName('left_button')
        self.btn_2.setObjectName('left_button')
        self.btn_3.setObjectName('left_button')
        self.btn_4.setObjectName('left_button')

        self.btn_1.clicked.connect(self.button1)
        self.btn_2.clicked.connect(self.button2)
        self.btn_3.clicked.connect(self.button3)
        self.btn_4.clicked.connect(self.button4)

        self.active_button = self.btn_1  # Set the initial active button

        # add tabs
        self.tab1 = self.ui1()
        self.tab2 = self.ui2()
        self.tab3 = self.ui3()
        self.tab4 = self.ui4()

        self.initUI()

    def initUI(self):
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.btn_1)
        left_layout.addWidget(self.btn_2)
        left_layout.addWidget(self.btn_3)
        left_layout.addWidget(self.btn_4)
        left_layout.addStretch(5)
        left_layout.setSpacing(20)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        self.right_widget = QTabWidget()
        self.right_widget.tabBar().setObjectName("mainTab")

        # Pass initial temporary values
        self.right_widget.addTab(self.tab1, '')
        self.right_widget.addTab(self.tab2, '')
        self.right_widget.addTab(self.tab3, '')
        self.right_widget.addTab(self.tab4, '')

        self.right_widget.setCurrentIndex(0)
        self.right_widget.setStyleSheet('''
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 10px; /* Adjust the border-radius value as needed */
                padding: 5px;
            }
            QTabBar::tab {
                width: 0;
                height: 0;
                margin: 0;
                padding: 0;
                border: none;
            }
        ''')

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.right_widget)
        main_layout.setStretch(0, 40)
        main_layout.setStretch(1, 200)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Initial button style update
        self.update_button_styles()

    def update_button_styles(self):
        # Define the common style for all buttons
        button_style = """
        QPushButton#left_button {
            border: none;
            background-color: #f0f0f0;
            padding: 10px;
        }
        QPushButton#left_button:hover {
            background-color: #d0d0d0;
        }
        QPushButton#left_button:focus {
            outline: none;
        }
        """
        # Define the active style for the active button
        active_style = """
        QPushButton#left_button[active="true"] {
            border-bottom: 2px solid #0000ff;
        }
        """

        # Apply the styles
        self.setStyleSheet(button_style + active_style)

        # Set the active property for the active button
        buttons = [self.btn_1, self.btn_2, self.btn_3, self.btn_4]
        for button in buttons:
            button.setProperty('active', False)
            button.style().unpolish(button)
            button.style().polish(button)

        self.active_button.setProperty('active', True)
        self.active_button.style().unpolish(self.active_button)
        self.active_button.style().polish(self.active_button)

    # Update active button method
    def set_active_button(self, button):
        self.active_button.setProperty('active', False)
        self.active_button.style().unpolish(self.active_button)
        self.active_button.style().polish(self.active_button)

        self.active_button = button

        self.active_button.setProperty('active', True)
        self.active_button.style().unpolish(self.active_button)
        self.active_button.style().polish(self.active_button)

    # ----------------- 
    # buttons

    def button1(self):
        self.right_widget.setCurrentIndex(0)
        self.set_active_button(self.btn_1)

    def button2(self):
        self.right_widget.setCurrentIndex(1)
        self.set_active_button(self.btn_2)

    def button3(self):
        self.right_widget.setCurrentIndex(2)
        self.set_active_button(self.btn_3)

    def button4(self):
        self.right_widget.setCurrentIndex(3)
        self.set_active_button(self.btn_4)

    # -----------------
    # pages

    def ui1(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel('page 1'))
        main_layout.addWidget(QLabel(f'Value 1: {self.temp_value1}'))
        main_layout.addWidget(QLabel(f'Value 2: {self.temp_value2}'))
        main_layout.addWidget(QLabel(f'Value 3: {self.temp_value3}'))
        
        # Add a button to update values
        update_button = QPushButton('Update Values', self)
        update_button.clicked.connect(self.update_values_from_another_function)
        main_layout.addWidget(update_button)
        
        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui2(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel('page 2'))
        main_layout.addWidget(QLabel(f'Value 1: {self.temp_value1}'))
        main_layout.addWidget(QLabel(f'Value 2: {self.temp_value2}'))
        main_layout.addWidget(QLabel(f'Value 3: {self.temp_value3}'))
        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main
        
    def ui3(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel('page 3'))
        main_layout.addWidget(QLabel(f'Value 1: {self.temp_value1}'))
        main_layout.addWidget(QLabel(f'Value 2: {self.temp_value2}'))
        main_layout.addWidget(QLabel(f'Value 3: {self.temp_value3}'))
        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    def ui4(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel('page 4'))
        main_layout.addWidget(QLabel(f'Value 1: {self.temp_value1}'))
        main_layout.addWidget(QLabel(f'Value 2: {self.temp_value2}'))
        main_layout.addWidget(QLabel(f'Value 3: {self.temp_value3}'))
        main_layout.addStretch(5)
        main = QWidget()
        main.setLayout(main_layout)
        return main

    # Method to update temporary values
    def update_temp_values(self, value1, value2, value3):
        self.temp_value1 = value1
        self.temp_value2 = value2
        self.temp_value3 = value3
        # Update UI to reflect new values
        self.tab1 = self.ui1()
        self.tab2 = self.ui2()
        self.tab3 = self.ui3()
        self.tab4 = self.ui4()
        self.right_widget.clear()
        self.right_widget.addTab(self.tab1, '')
        self.right_widget.addTab(self.tab2, '')
        self.right_widget.addTab(self.tab3, '')
        self.right_widget.addTab(self.tab4, '')

    # Function to update values from another function or event
    def update_values_from_another_function(self):
        # New values
        new_value1 = 10
        new_value2 = 20
        new_value3 = 'Updated'
        # Call update_temp_values() with new values
        self.update_temp_values(new_value1, new_value2, new_value3)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec_())
