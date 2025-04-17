# main.py
# Entry point: launches the Qt application with integrated asyncio loop via qasync

import sys
import asyncio
from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop
from ui import MainWindow  # Interface utilisateur définie dans ui.py
import signaling_server  # démarre le signaling server en tâche de fond


if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Lancement non bloquant du serveur de signalisation
    loop.create_task(signaling_server.start())

    # Création de la fenêtre principale
    window = MainWindow(loop)
    window.show()

    # Boucle principale de l'application
    with loop:
        loop.run_forever()