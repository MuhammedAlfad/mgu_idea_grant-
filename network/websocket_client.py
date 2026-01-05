import json
import time
import websocket

from PyQt5.QtCore import QThread, pyqtSignal


class WebSocketClient(QThread):
    """
    Background WebSocket client that listens for backend messages
    and safely emits them to the UI using Qt signals.
    """

    message_received = pyqtSignal(dict)
    connection_status = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self._running = True

    def run(self):
        """
        Thread entry point.
        Continuously tries to connect and listen to WebSocket messages.
        Auto-reconnects on failure.
        """
        while self._running:
            try:
                ws = websocket.WebSocket()
                ws.connect(self.url)
                self.connection_status.emit("Connected")

                while self._running:
                    message = ws.recv()
                    data = json.loads(message)
                    self.message_received.emit(data)

            except Exception as e:
                print("WebSocket error:", e)
                self.connection_status.emit("Disconnected")
                time.sleep(3)

    def stop(self):
        """
        Safely stop the WebSocket thread.
        """
        self._running = False
        self.quit()
        self.wait()
