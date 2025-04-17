# RemotePlay Project

## Description
RemotePlay est une application qui permet de partager des entrées de souris et de clavier entre un hôte et un client distant via une interface utilisateur Qt. L'application utilise WebRTC pour la communication en temps réel et gère les connexions via un serveur de signalisation basé sur WebSocket.

## Structure du projet
Le projet est organisé comme suit :

```
├── RemotePlay
│   ├── main.py           # Point d'entrée de l'application.
│   ├── ui.py             # Définit l'interface utilisateur principale.
│   ├── utils.py          # Contient des fonctions utilitaires.
│   ├── signaling_server.py # Met en place le serveur de signalisation.
│   ├── network.py        # Gère les pairs hôte et distant.
│   ├── host.py           # Interface utilisateur pour l'hôte.
│   ├── remote.py         # Interface utilisateur pour le client distant.
│   ├── streaming.py      # Gère la capture et l'envoi de vidéo et d'audio.
│   └── input_handler.py   # Capture et rejoue les événements d'entrée.
├── requirements.txt      # Liste des dépendances nécessaires.
└── README.md             # Documentation du projet.
```

## Installation
Pour installer les dépendances nécessaires, exécutez la commande suivante :

```
pip install -r requirements.txt
```

## Utilisation
1. Lancez le serveur de signalisation en exécutant `src/signaling_server.py`.
2. Ouvrez deux instances de l'application :
   - Une pour l'hôte en exécutant `src/host.py`.
   - Une pour le client distant en exécutant `src/remote.py`.
3. L'hôte peut générer un code d'accès et le partager avec le client distant.
4. Le client distant peut entrer le code d'accès pour se connecter à l'hôte.

## Contribuer
Les contributions sont les bienvenues ! Veuillez soumettre une demande de tirage pour toute amélioration ou correction de bogue.

## License
Ce projet est sous licence MIT. Veuillez consulter le fichier LICENSE pour plus de détails.