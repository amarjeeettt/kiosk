import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QMenu, QVBoxLayout, QAction

class DropdownButton(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create a QPushButton
        self.pushButton = QPushButton("Dropdown Button", self)
        
        # Adjust the size of the push button
        self.pushButton.setFixedSize(150, 50)  # width: 150px, height: 50px

        # Create a QMenu
        self.menu = QMenu(self)
        
        # Create actions for the menu
        self.action1 = QAction("Option 1", self)
        self.action2 = QAction("Option 2", self)
        self.action3 = QAction("Option 3", self)
        
        # Connect actions to their respective slots
        self.action1.triggered.connect(lambda: self.on_action_triggered(self.action1))
        self.action2.triggered.connect(lambda: self.on_action_triggered(self.action2))
        self.action3.triggered.connect(lambda: self.on_action_triggered(self.action3))
        
        # Add actions to the menu
        self.menu.addAction(self.action1)
        self.menu.addAction(self.action2)
        self.menu.addAction(self.action3)
        
        # Set the menu to the push button
        self.pushButton.setMenu(self.menu)

        # Adjust the menu's properties
        self.menu.aboutToHide.connect(self.menu.hide)
        self.menu.aboutToShow.connect(self.menu.show)

        # Use a stylesheet to make the menu appear below the button
        self.menu.setStyleSheet("""
            QMenu {
                left: 0;
            }
        """)

        # Call the function associated with Option 1
        self.on_action_triggered(self.action1)

        # Create a layout and add the button to the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.pushButton)
        
    # Slot for actions
    def on_action_triggered(self, action):
        self.pushButton.setText(action.text())
        print(f"Action '{action.text()}' triggered")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = DropdownButton()
    window.show()
    sys.exit(app.exec_())
