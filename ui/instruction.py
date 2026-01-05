from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QFrame,
    QPushButton
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal


STATE_COLORS = {
    "TOO_FAR": "red",
    "TOO_CLOSE": "orange",
    "PERFECT": "green",
    "CAPTURING": "blue",
    "PROCESSING": "blue"
}


class InstructionView(QWidget):
    """
    Dummy Instruction View
    Follows the exact project instructions.
    """

    back_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.setFixedWidth(80)
        self.back_button.clicked.connect(self._on_back_clicked)

        # Connection status
        self.connection_label = QLabel("Connected (Demo Mode)")
        self.connection_label.setAlignment(Qt.AlignCenter)
        self.connection_label.setStyleSheet("color: green;")

        # Instruction text
        self.instruction_label = QLabel("Waiting...")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        # Distance
        self.distance_label = QLabel("Distance: -- cm")
        self.distance_label.setAlignment(Qt.AlignCenter)

        # Tilt
        self.tilt_label = QLabel("Tilt: --")
        self.tilt_label.setAlignment(Qt.AlignCenter)

        # Mode
        self.mode_label = QLabel("Mode: --")
        self.mode_label.setAlignment(Qt.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Result
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 18px;")

        self.confidence_label = QLabel("")
        self.confidence_label.setAlignment(Qt.AlignCenter)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.back_button, alignment=Qt.AlignLeft)
        layout.addWidget(self.connection_label)
        layout.addSpacing(10)
        layout.addWidget(self.instruction_label)
        layout.addSpacing(10)
        layout.addWidget(self.distance_label)
        layout.addWidget(self.tilt_label)
        layout.addWidget(self.mode_label)
        layout.addSpacing(15)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(15)
        layout.addWidget(divider)
        layout.addSpacing(10)
        layout.addWidget(self.result_label)
        layout.addWidget(self.confidence_label)
        layout.addStretch()

        self.setLayout(layout)

        # Dummy demo data
        self.demo_steps = [
            ("Move palm closer", "TOO_FAR", "LEFT", 18.5),
            ("Hold steady", "PERFECT", "STRAIGHT", 9.2),
            ("Tilt right", "PERFECT", "RIGHT", 9.0),
            ("Capturing image", "CAPTURING", "STRAIGHT", 8.8),
            ("Processing", "PROCESSING", "STRAIGHT", 8.8),
        ]

        self.demo_index = 0
        self.demo_progress = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self._run_demo)

    def start_demo(self, mode="Matching"):
        self.mode_label.setText(f"Mode: {mode}")
        self.demo_index = 0
        self.demo_progress = 0
        self.progress_bar.setValue(0)
        self.result_label.setText("")
        self.confidence_label.setText("")
        self.timer.start(1200)

    def stop_demo(self):
        self.timer.stop()

    def _run_demo(self):
        if self.demo_index < len(self.demo_steps):
            text, state, tilt, dist = self.demo_steps[self.demo_index]

            self.instruction_label.setText(text)
            self.instruction_label.setStyleSheet(
                f"font-size: 22px; font-weight: bold; color: {STATE_COLORS[state]};"
            )

            self.distance_label.setText(f"Distance: {dist} cm")
            self.tilt_label.setText(f"Tilt: {tilt}")

            self.demo_progress += 20
            self.progress_bar.setValue(self.demo_progress)

            self.demo_index += 1
        else:
            self.timer.stop()
            self.result_label.setText("MATCH")
            self.confidence_label.setText("Confidence: 92.3%")

    def _on_back_clicked(self):
        self.stop_demo()
        self.back_clicked.emit()
