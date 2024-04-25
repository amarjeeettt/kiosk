from PyQt5.QtWidgets import QMessageBox
from cups import Connection


def check_printer_connection():
    # Initialize a cups connection
    conn = Connection()

    # Get the list of printers
    printers = conn.getPrinters()

    # Check if there are any printers connected
    if not printers:
        # If no printers are connected, show a message box with the parent window
        return True
    else:
        return False
