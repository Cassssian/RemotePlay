# remote.py
# Remote UI: input code, paste, search, join, and status

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QApplication
from PyQt5.QtCore import Qt
from network import RemotePeer

class RemoteWindow(QMainWindow):
    def __init__(self, username, loop):
        super().__init__()
        self.loop = loop
        self.username = username
        self.setWindowTitle("Accéder - RemotePlay")
        self._build_ui()
        self.peer = None

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        paste_row = QHBoxLayout()
        self.code_edit = QLineEdit()
        paste_btn = QPushButton("📋 Coller")
        paste_btn.clicked.connect(lambda: self.code_edit.setText(QApplication.clipboard().text()))
        paste_row.addWidget(self.code_edit)
        paste_row.addWidget(paste_btn)
        layout.addLayout(paste_row)

        validate_btn = QPushButton("Valider")
        validate_btn.clicked.connect(self._on_validate)
        layout.addWidget(validate_btn)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def _on_validate(self):
        self.peer = RemotePeer(self.username, self.code_edit.text(), self, self.loop)

    def show_remote_info(self, host_name):
        self.status_label.setText(f"Hôte: {host_name}")

    def enable_join(self):
        join_btn = QPushButton("Rejoindre")
        join_btn.clicked.connect(lambda: self.peer.join())
        self.layout().addWidget(join_btn)
