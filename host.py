# host.py
# Host UI: shows access code, user statuses, and ready toggle

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from network import HostPeer
from utils import generate_color_scheme

class HostWindow(QMainWindow):
    def __init__(self, username, loop):
        super().__init__()
        self.loop = loop
        self.username = username
        self.setWindowTitle("Héberger - RemotePlay")
        self.color_scheme = generate_color_scheme()  # Génère un schéma de couleurs
        self._build_ui()
        self.peer = HostPeer(username, self, loop)

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

        # Code d'accès
        self.code_label = QLabel("Code: ")
        self.code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.code_label.mousePressEvent = lambda e: QApplication.clipboard().setText(self.code_label.text())
        layout.addWidget(self.code_label)

        # Statut
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Bouton prêt/pas prêt
        self.ready_btn = QPushButton("Pas prêt")
        self.ready_btn.setVisible(False)  # Caché par défaut
        self.ready_btn.clicked.connect(lambda: self.peer.toggle_ready())
        layout.addWidget(self.ready_btn)

        # Bouton relancer
        self.retry_btn = QPushButton("Relancer")
        self.retry_btn.setVisible(False)  # Caché par défaut
        self.retry_btn.clicked.connect(self._on_retry)
        layout.addWidget(self.retry_btn)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def show_code(self, code):
        self.code_label.setText(code)

    def show_status(self, text):
        self.status_label.setText(text)

    def show_error(self, text):
        QMessageBox.critical(self, "Erreur", text)

    def enable_ready_button(self):
        self.ready_btn.setVisible(True)

    def enable_retry_button(self):
        self.retry_btn.setVisible(True)

    def _on_retry(self):
        self.retry_btn.setVisible(False)
        self.status_label.setText("Relance de la recherche...")
        self.peer = HostPeer(self.username, self, self.loop)  # Relance la recherche
