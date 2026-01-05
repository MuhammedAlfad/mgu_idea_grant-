from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal, Qt


class HomeView(QWidget):
    """
    Home screen of the application.
    Displays app title, connection status, and control buttons.
    Emits signals when buttons are clicked.
    """

    register_clicked = pyqtSignal()
    match_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Title
        self.title_label = QLabel("Palm Authentication System")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")

        # Connection status
        self.connection_label = QLabel("Disconnected")
        self.connection_label.setAlignment(Qt.AlignCenter)
        self.connection_label.setStyleSheet("color: red; font-size: 14px;")

        # Buttons
        self.register_button = QPushButton("Register")
        self.match_button = QPushButton("Match")
        self.stop_button = QPushButton("Stop")

        self.register_button.setMinimumHeight(40)
        self.match_button.setMinimumHeight(40)
        self.stop_button.setMinimumHeight(40)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.match_button)
        button_layout.addWidget(self.stop_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(self.title_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.connection_label)
        main_layout.addSpacing(30)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

        # Signal connections
        self.register_button.clicked.connect(self.register_clicked.emit)
        self.match_button.clicked.connect(self.match_clicked.emit)
        self.stop_button.clicked.connect(self.stop_clicked.emit)

    def set_connection_status(self, status: str):
        """
        Update connection status label.
        """
        self.connection_label.setText(status)
        if status == "Connected":
            self.connection_label.setStyleSheet("color: green; font-size: 14px;")
        else:
            self.connection_label.setStyleSheet("color: red; font-size: 14px;")
