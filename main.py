import sys
import cups
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QDesktopWidget,
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QMovie
from home_screen_widget import HomeScreenWidget
from admin_login import AdminLoginWidget
from admin_window import AdminWindowWidget
from view_form import ViewFormWidget
from print_preview import PrintPreviewWidget
from view_process import ViewProcessWidget
from print_form import PrintFormWidget
from about import AboutWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.set_background_image()
        self.setWindowTitle("Pay-per Print")

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.setup_ui()

        self.printer_state = None
        self.is_printer_available()

    def setup_ui(self):
        self.layout = QVBoxLayout(self.centralWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)

        self.movie = QMovie("./img/slideshow.gif")
        self.label.setMovie(self.movie)

        self.movie.start()

        self.movie.finished.connect(self.movie.start)

        self.layout.addWidget(self.label)
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.resizeEvent(None)

    def mousePressEvent(self, event):
        if self.label.isVisible():
            self.label.hide()
            self.movie.stop()
            self.show_home_screen()

    def resizeEvent(self, event):
        screen_size = QApplication.primaryScreen().size()
        self.label.setFixedSize(screen_size)
        self.movie.setScaledSize(screen_size)
        if event:
            event.accept()

    def go_back_to_slideshow(self):
        self.label.show()
        self.movie.start()
        self.movie.finished.connect(self.movie.start)
        self.is_printer_available()

    def show_home_screen(self):
        self.home_screen_widget = HomeScreenWidget(self)
        self.layout.addWidget(self.home_screen_widget)

        self.home_screen_widget.show()

        self.home_screen_widget.start_button_clicked.connect(self.show_form_list)
        self.home_screen_widget.admin_button_clicked.connect(self.show_admin_login)
        self.home_screen_widget.about_button_clicked.connect(self.show_about)
        self.home_screen_widget.go_back_clicked.connect(self.go_back_to_slideshow)

    def show_about(self):
        self.about_widget = AboutWidget(self)
        self.layout.addWidget(self.about_widget)

        self.home_screen_widget.setVisible(False)

        self.about_widget.show()

        self.about_widget.backbt_clicked.connect(self.show_home_screen)

    def show_admin_login(self):
        self.admin_login = AdminLoginWidget(self)
        self.layout.addWidget(self.admin_login)

        self.home_screen_widget.setVisible(False)

        self.admin_login.show()

        self.admin_login.login_clicked.connect(self.show_admin_window)
        self.admin_login.home_screen_backbt_clicked.connect(self.show_home_screen)

    def show_admin_window(self):
        self.admin_window = AdminWindowWidget(self, self.printer_state)
        self.layout.addWidget(self.admin_window)

        self.admin_login.setVisible(False)

        self.admin_window.show()

        self.admin_window.home_screen_backbt_clicked.connect(self.show_home_screen)

    def show_form_list(self):
        self.view_form = ViewFormWidget(self, self.printer_state)
        self.layout.addWidget(self.view_form)

        self.home_screen_widget.setVisible(False)

        self.view_form.show()
        self.view_form.view_button_clicked.connect(self.show_print_preview)
        self.view_form.go_back_clicked.connect(self.show_home_screen)

    @pyqtSlot(str, int, bool, bool, bool)
    def show_print_preview(
        self, title, page_number, printer_status, bondpaper_status, ink_status
    ):
        self.print_preview = PrintPreviewWidget(
            self, title, page_number, printer_status, bondpaper_status, ink_status
        )
        self.layout.addWidget(self.print_preview)

        self.view_form.setVisible(False)

        self.print_preview.show()
        self.print_preview.view_form_backbt_clicked.connect(self.show_form_list)
        self.print_preview.view_process_clicked.connect(self.show_view_process)
        self.print_preview.print_form_clicked.connect(self.show_print_form)

    @pyqtSlot(str, int, int, int)
    def show_print_form(self, title, num_copy, num_pages, total):
        self.print_form = PrintFormWidget(self, title, num_copy, num_pages, total)
        self.layout.addWidget(self.print_form)

        self.print_preview.setVisible(False)

        self.print_form.show()

        self.print_form.cancel_clicked.connect(self.go_back_print_preview_print_form)
        self.print_form.go_back_home.connect(self.go_back_to_slideshow)

    @pyqtSlot(str)
    def show_view_process(self, title):
        self.view_process = ViewProcessWidget(self, title)
        self.layout.addWidget(self.view_process)

        self.print_preview.setVisible(False)

        self.view_process.show()
        self.view_process.print_preview_backbt_clicked.connect(
            self.go_back_print_preview
        )

    def go_back_print_preview(self):
        self.print_preview.show()

    def go_back_print_preview_print_form(self):
        self.print_preview.show()

    def is_printer_available(self):
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()

            if not printers:
                self.printer_state = False
                raise Exception("No printers available.")

            idle_printer_found = False
            for printer_name, printer_attributes in printers.items():
                if (
                    "printer-state" in printer_attributes
                    and printer_attributes["printer-state"] == 3
                ):
                    idle_printer_found = True
                    self.printer_state = True
                    break

            if not idle_printer_found:
                self.printer_state = False
                raise Exception("No idle printer available")

        except Exception as e:
            print("Error during printing:", e)

    def set_background_image(self):
        # Get screen resolution
        screen_resolution = QDesktopWidget().screenGeometry()

        # Load the background image
        pixmap = QPixmap("./img/background.jpg")

        # Resize the background image to fit the screen resolution
        pixmap = pixmap.scaled(
            screen_resolution.width(), screen_resolution.height(), Qt.IgnoreAspectRatio
        )

        # Create a label to display the background image
        background_label = QLabel(self)
        background_label.setPixmap(pixmap)
        background_label.setGeometry(
            0, 0, screen_resolution.width(), screen_resolution.height()
        )  # Set label size to screen resolution
        background_label.setScaledContents(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    sys.exit(app.exec_())
