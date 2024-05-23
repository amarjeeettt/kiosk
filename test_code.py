import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget

class ExampleWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("QTextBrowser Example")
        self.setGeometry(100, 100, 800, 600)

        # Create a QTextBrowser widget
        self.text_browser = QTextBrowser()
        
        # Set the style sheet to remove background and border
        self.text_browser.setStyleSheet("QTextBrowser { border: none; background: transparent; }")

        # Set some HTML content
        html_content = """
        <h1>Welcome to QTextBrowser</h1>
        <p>This is an example of using <b>QTextBrowser</b> to display HTML content.</p>
        <p>You can include various HTML elements such as:</p>
        <ul>
            <li>Lists</li>
            <li><a href="#section1">Links</a></li>
            <li>Images</li>
        </ul>
        <p>Click the link to go to <a href="#section1">Section 1</a>.</p>
        <h2 id="section1">Section 1</h2>
        <p>This is Section 1. <a href="#top">Back to top</a>.</p>
        """
        self.text_browser.setHtml(html_content)

        # Create a layout and add the text browser to it
        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

# Create the application instance
app = QApplication(sys.argv)

# Create and show the main window
window = ExampleWindow()
window.show()

# Run the application event loop
sys.exit(app.exec_())
