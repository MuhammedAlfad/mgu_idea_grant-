import sys
import requests
import socketio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QProgressBar, QStackedWidget, QFrame, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# --- Configuration ---
BACKEND_URL = "http://localhost:5000"
SIO_URL = "http://localhost:5000"

# --- Stylesheet (Matches your Green/White Theme) ---
STYLESHEET = """
    QMainWindow { background-color: #f5f5f5; }
    QWidget { font-family: 'Segoe UI', sans-serif; }
    QLabel#Title { font-size: 24px; font-weight: bold; color: #2E7D32; }
    QLabel#Status { font-size: 14px; color: #666; }
    QLabel#Instruction { font-size: 32px; font-weight: bold; qproperty-alignment: AlignCenter; }
    QLabel#DataLabel { font-size: 16px; color: #333; font-weight: bold; }
    QLabel#ValueLabel { font-size: 16px; color: #555; }
    QLineEdit { padding: 10px; border: 2px solid #ccc; border-radius: 5px; font-size: 14px; }
    QLineEdit:focus { border: 2px solid #2E7D32; }
    QPushButton { background-color: #2E7D32; color: white; border-radius: 6px; padding: 12px; font-size: 16px; font-weight: bold; }
    QPushButton:hover { background-color: #388E3C; }
    QPushButton#StopBtn { background-color: #D32F2F; }
    QPushButton#StopBtn:hover { background-color: #E53935; }
    QProgressBar { border: 2px solid #ccc; border-radius: 5px; text-align: center; height: 25px; }
    QProgressBar::chunk { background-color: #2E7D32; }
    QFrame#Card { background-color: white; border-radius: 10px; border: 1px solid #ddd; }
"""

# --- Network Worker (Handles WebSocket in Background) ---
class SocketWorker(QThread):
    update_signal = pyqtSignal(dict)
    connection_signal = pyqtSignal(bool)

    def run(self):
        self.sio = socketio.Client()

        @self.sio.event
        def connect():
            self.connection_signal.emit(True)

        @self.sio.event
        def disconnect():
            self.connection_signal.emit(False)

        @self.sio.on('status_update')
        def on_message(data):
            self.update_signal.emit(data)

        while True:
            try:
                self.sio.connect(SIO_URL)
                self.sio.wait()
            except Exception:
                self.connection_signal.emit(False)
                self.sleep(2)

# --- View 1: Home Screen ---
class HomeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Enter User ID (for Register)")
        
        self.btn_register = QPushButton("Start Registration")
        self.btn_match = QPushButton("Start Matching")

        card_layout.addWidget(QLabel("User Management"))
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.btn_register)
        card_layout.addWidget(self.btn_match)
        
        layout.addWidget(card)

# --- View 2: Instruction Screen ---
class InstructionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.lbl_instruction = QLabel("Ready")
        self.lbl_instruction.setObjectName("Instruction")
        self.lbl_instruction.setWordWrap(True)
        self.lbl_instruction.setFixedHeight(100)
        
        # Data Grid
        grid_frame = QFrame()
        grid_frame.setObjectName("Card")
        grid_layout = QVBoxLayout(grid_frame)
        
        self.val_mode = self.create_row(grid_layout, "Mode:")
        self.val_dist = self.create_row(grid_layout, "Distance:")
        self.val_tilt = self.create_row(grid_layout, "Tilt:")
        self.val_conf = self.create_row(grid_layout, "Confidence:")
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        
        self.btn_stop = QPushButton("STOP")
        self.btn_stop.setObjectName("StopBtn")

        layout.addStretch()
        layout.addWidget(self.lbl_instruction)
        layout.addSpacing(20)
        layout.addWidget(grid_frame)
        layout.addSpacing(20)
        layout.addWidget(self.progress)
        layout.addStretch()
        layout.addWidget(self.btn_stop)

    def create_row(self, layout, text):
        row = QHBoxLayout()
        lbl = QLabel(text)
        lbl.setObjectName("DataLabel")
        val = QLabel("--")
        val.setObjectName("ValueLabel")
        val.setAlignment(Qt.AlignRight)
        row.addWidget(lbl)
        row.addWidget(val)
        layout.addLayout(row)
        return val

# --- Main Window Controller ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palm Auth Controller")
        self.resize(500, 600)
        self.setStyleSheet(STYLESHEET)
        
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Header
        self.header_layout = QHBoxLayout()
        self.title_label = QLabel("Palm ID System")
        self.title_label.setObjectName("Title")
        self.status_label = QLabel("🔴 Disconnected")
        self.status_label.setObjectName("Status")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addWidget(self.status_label)
        self.main_layout.addLayout(self.header_layout)

        # Stacked Views
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.home = HomeView()
        self.instr = InstructionView()
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.instr)

        # Connect Buttons
        self.home.btn_register.clicked.connect(self.start_register)
        self.home.btn_match.clicked.connect(self.start_match)
        self.instr.btn_stop.clicked.connect(self.stop_process)

        # Start Networking
        self.worker = SocketWorker()
        self.worker.update_signal.connect(self.update_ui)
        self.worker.connection_signal.connect(self.update_connection)
        self.worker.start()

    def update_connection(self, connected):
        if connected:
            self.status_label.setText("🟢 Connected")
            self.status_label.setStyleSheet("color: green;")
            self.home.btn_register.setEnabled(True)
            self.home.btn_match.setEnabled(True)
        else:
            self.status_label.setText("🔴 Disconnected")
            self.status_label.setStyleSheet("color: red;")
            self.home.btn_register.setEnabled(False)
            self.home.btn_match.setEnabled(False)

    def start_register(self):
        user_id = self.home.user_input.text().strip()
        if not user_id:
            QMessageBox.warning(self, "Input Error", "Please enter a User ID")
            return
        self.send_command('/start_register', {'user_id': user_id})
        self.stack.setCurrentIndex(1)

    def start_match(self):
        self.send_command('/start_match', {})
        self.stack.setCurrentIndex(1)

    def stop_process(self):
        self.send_command('/stop', {})
        self.instr.lbl_instruction.setText("Stopped")
        self.stack.setCurrentIndex(0)

    def send_command(self, endpoint, payload):
        try:
            requests.post(f"{BACKEND_URL}{endpoint}", json=payload)
        except Exception as e:
            print(f"Error: {e}")

    def update_ui(self, data):
        # Update logic mapping backend data to frontend labels
        self.instr.lbl_instruction.setText(data.get('text', ''))
        self.instr.val_mode.setText(data.get('mode', '--').upper())
        self.instr.val_dist.setText(f"{data.get('distance_cm', 0)} cm")
        self.instr.val_tilt.setText(data.get('tilt', 'NONE'))
        self.instr.progress.setValue(data.get('progress', 0))
        
        if data.get('confidence'):
            self.instr.val_conf.setText(f"{data.get('confidence')*100:.1f}%")
        
        # Color Logic
        state = data.get('state', 'NONE')
        color = "#333"
        if state == "TOO_FAR": color = "#D32F2F"      # Red
        elif state == "TOO_CLOSE": color = "#F57C00"  # Orange
        elif state == "PERFECT": color = "#388E3C"    # Green
        elif state == "CAPTURING": color = "#1976D2"  # Blue
        
        self.instr.lbl_instruction.setStyleSheet(f"color: {color};")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())