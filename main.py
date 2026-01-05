import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QInputDialog
)

from ui.home import HomeView
from ui.instruction import InstructionView


class MainWindow(QMainWindow):
    """
    Main application window.
    Single window with dynamic content switching.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Palm Authentication GUI")
        self.resize(500, 520)

        # Stacked widget (single window)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Views
        self.home_view = HomeView()
        self.instruction_view = InstructionView()

        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.instruction_view)

        # Start on Home screen
        self.stack.setCurrentWidget(self.home_view)

        # Home button connections
        self.home_view.register_clicked.connect(self.on_register_clicked)
        self.home_view.match_clicked.connect(self.on_match_clicked)
        self.home_view.stop_clicked.connect(self.on_stop_clicked)

        # Back button from Instruction view
        self.instruction_view.back_clicked.connect(self.on_back_clicked)

    # ---------------------------
    # Button Handlers
    # ---------------------------

    def on_register_clicked(self):
        """
        Registration flow (dummy mode).
        """
        user_id, ok = QInputDialog.getText(
            self,
            "Register User",
            "Enter User ID:"
        )

        if ok and user_id.strip():
            self.stack.setCurrentWidget(self.instruction_view)
            self.instruction_view.start_demo("Registration")

    def on_match_clicked(self):
        """
        Matching flow (dummy mode).
        """
        self.stack.setCurrentWidget(self.instruction_view)
        self.instruction_view.start_demo("Matching")

    def on_stop_clicked(self):
        """
        Stop current operation and return to Home.
        """
        self.stack.setCurrentWidget(self.home_view)

    def on_back_clicked(self):
        """
        Back button from Instruction view.
        """
        self.stack.setCurrentWidget(self.home_view)

    # ---------------------------
    # Clean Exit
    # ---------------------------

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
