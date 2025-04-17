# host.py
# Host UI: shows access code, user statuses, and ready toggle

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QApplication
from PyQt5.QtCore import Qt
from network import HostPeer

class HostWindow(QMainWindow):
    def __init__(self, username, loop):
        super().__init__()
        self.loop = loop
        self.username = username
        self.setWindowTitle("Héberger - RemotePlay")
        self._build_ui()
        self.peer = HostPeer(username, self, loop)

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        self.code_label = QLabel("Code: ")
        self.code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.code_label.mousePressEvent = lambda e: QApplication.clipboard().setText(self.code_label.text())
        layout.addWidget(self.code_label)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.ready_btn = QPushButton("Pas prêt")
        self.ready_btn.clicked.connect(lambda: self.peer.toggle_ready())
        layout.addWidget(self.ready_btn)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def show_code(self, code):
        self.code_label.setText(code)

    def show_status(self, text):
        self.status_label.setText(text)

    def show_error(self, text):
        QMessageBox.critical(self, "Erreur", text)
