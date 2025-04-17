# remote.py
# Remote UI: input code, paste, search, join, and status

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QApplication
from PyQt5.QtCore import Qt
from network import RemotePeer
from utils import generate_color_scheme

class RemoteWindow(QMainWindow):
    def __init__(self, username, loop):
        super().__init__()
        self.loop = loop
        self.username = username
        self.setWindowTitle("Accéder - RemotePlay")
        self.color_scheme = generate_color_scheme()  # Génère un schéma de couleurs
        self._build_ui()
        self.peer = None
        self.retry_button = QPushButton("Relancer", self)
        self.retry_button.setEnabled(False)
        self.retry_button.clicked.connect(self.retry_search)

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        # Appliquer le style dynamique
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.color_scheme['background']};
                color: {self.color_scheme['text']};
            }}
            QLabel {{
                font-size: 16px;
                color: {self.color_scheme['primary']};
            }}
            QPushButton {{
                background-color: {self.color_scheme['primary']};
                color: {self.color_scheme['text']};
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {self.color_scheme['secondary']};
            }}
        """)

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

        self.join_button = QPushButton("Rejoindre")
        self.join_button.setEnabled(False)
        self.join_button.clicked.connect(lambda: self.peer.join())
        layout.addWidget(self.join_button)

        layout.addWidget(self.retry_button)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def _on_validate(self):
        self.peer = RemotePeer(self.username, self.code_edit.text(), self, self.loop)

    def show_remote_info(self, username):
        self.status_label.setText(f"Connecté à l'hôte : {username}")

    def enable_join(self):
        self.join_button.setEnabled(True)

    def show_status(self, text):
        self.status_label.setText(text)

    def enable_retry(self):
        self.retry_button.setEnabled(True)

    def retry_search(self):
        self.retry_button.setEnabled(False)
        self.status_label.setText("Relance de la recherche...")
        self.parent().start_search()  # Exemple, ajustez selon votre logique
