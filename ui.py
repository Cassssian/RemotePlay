# ui.py
# Defines the main menu UI and navigation to host/connect pages

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from utils import random_username

class MainWindow(QMainWindow):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.setWindowTitle("RemotePlay")
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        # Username row
        user_row = QHBoxLayout()
        self.user_edit = QLineEdit("Player")
        user_row.addWidget(QLabel("Nom d'utilisateur:"))
        user_row.addWidget(self.user_edit)
        rand_btn = QPushButton("🎲")
        rand_btn.clicked.connect(self._on_random)
        user_row.addWidget(rand_btn)
        layout.addLayout(user_row)

        # Host / Connect buttons
        btn_row = QHBoxLayout()
        host_btn = QPushButton("Héberger")
        host_btn.clicked.connect(self._on_host)
        connect_btn = QPushButton("Accéder")
        connect_btn.clicked.connect(self._on_connect)
        btn_row.addWidget(host_btn)
        btn_row.addWidget(connect_btn)
        layout.addLayout(btn_row)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def _on_random(self):
        self.user_edit.setText(random_username())

    def _on_host(self):
        from host import HostWindow
        self.host_win = HostWindow(self.user_edit.text(), self.loop)
        self.host_win.show()
        self.close()

    def _on_connect(self):
        from remote import RemoteWindow
        self.remote_win = RemoteWindow(self.user_edit.text(), self.loop)
        self.remote_win.show()
        self.close()
