# network.py
# Peer classes for host and remote: manage signaling and WebRTC

import asyncio
import json
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceServer, RTCConfiguration
from utils import generate_access_code
from streaming import ScreenTrack, AudioTrack  # Import des flux vidéo et audio
from input_handler import InputHandler

SIGNALING_URL = 'wss://signaling-server-y7w0.onrender.com'

class BasePeer:
    def __init__(self, username, window, loop):
        self.username = username
        self.window = window
        self.loop = loop

        # Utilisation de RTCConfiguration avec RTCIceServer
        ice_servers = [
            RTCIceServer(urls="stun:stun.l.google.com:19302"),  # Serveur STUN public
            RTCIceServer(urls = "turn:turn.bistri.com:80", username = "homeo", credential = "homeo")  # Exemple de serveur TURN
        ]
        self.pc = RTCPeerConnection(RTCConfiguration(ice_servers))
        self.channel = None

    async def _connect_signaling(self):
        try:
            self.ws = await websockets.connect(SIGNALING_URL)
            return True
        except Exception as e:
            self.window.show_error(f"Impossible de joindre le signaling server : {e}")
            return False

    async def _setup(self):
        # Exemple d'ajout de piste
        self.pc.addTrack(self.screen_track)

class HostPeer(BasePeer):
    def __init__(self, username, window, loop):
        super().__init__(username, window, loop)
        asyncio.create_task(self._setup())

    async def _setup(self):
        if not await self._connect_signaling():
            return
        code = generate_access_code({'username': self.username})
        await self.ws.send(json.dumps({'action': 'register', 'code': code, 'username': self.username}))
        self.window.show_code(code)

        # Ajout du flux vidéo
        self.screen_track = ScreenTrack()
        self.pc.addTrack(self.screen_track)

        @self.pc.on("datachannel")
        def on_datachannel(channel):
            self.channel = channel

            @channel.on("message")
            def on_message(message):
                try:
                    data = json.loads(message)
                    event_type = data.get('type')
                    if event_type == 'key_press':
                        print(f"Touche pressée : {data.get('key')}")
                    elif event_type == 'key_release':
                        print(f"Touche relâchée : {data.get('key')}")
                    elif event_type == 'mouse_move':
                        print(f"Souris déplacée : x={data.get('x')}, y={data.get('y')}")
                    elif event_type == 'mouse_click':
                        print(f"Clic souris : x={data.get('x')}, y={data.get('y')}, bouton={data.get('button')}, appuyé={data.get('pressed')}")
                    elif event_type == 'joystick_axis':
                        print(f"Joystick : axe={data.get('axis')}, valeur={data.get('value')}")
                    elif event_type == 'joystick_button':
                        print(f"Bouton joystick : bouton={data.get('button')}, appuyé={data.get('pressed')}")
                    elif event_type == 'joystick_hat':
                        print(f"Joystick hat : hat={data.get('hat')}, valeur={data.get('value')}")
                    elif event_type == 'joystick_axis':
                        print(f"Joystick : axe={data.get('axis')}, valeur={data.get('value')}")
                    elif event_type == 'joystick_button':
                        print(f"Bouton joystick : bouton={data.get('button')}, appuyé={data.get('pressed')}")
                    elif event_type == 'joystick_hat':
                        print(f"Joystick hat : hat={data.get('hat')}, valeur={data.get('value')}")
                    elif event_type == 'joystick_axis':
                        print(f"Joystick : axe={data.get('axis')}, valeur={data.get('value')}")
                    elif event_type == 'joystick_button':
                        print(f"Bouton joystick : bouton={data.get('button')}, appuyé={data.get('pressed')}")
                    elif event_type == 'joystick_hat':
                        print(f"Joystick hat : hat={data.get('hat')}, valeur={data.get('value')}")
                except Exception as e:
                    print(f"Erreur lors de la réception du message : {e}")

        timeout = 150  # Temps total en secondes
        for remaining in range(timeout, 0, -1):
            self.window.show_status(f"En attente d'une connexion... ({remaining}s restantes)")
            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=1)
                data = json.loads(msg)
                if data.get('action') == 'remote_found':
                    self.window.show_status(f"Connecté à : {data.get('username')}")
                    self.window.enable_ready_button()
                    await self._negotiate_offer()
                    return
            except asyncio.TimeoutError:
                continue

        self.window.show_status("Timeout : aucun client")
        self.window.enable_retry_button()

    async def _negotiate_offer(self):
        self.channel = self.pc.createDataChannel('input')
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        await self.ws.send(json.dumps({'action': 'offer', 'sdp': self.pc.localDescription.sdp, 'type': self.pc.localDescription.type}))

        async for msg in self.ws:
            data = json.loads(msg)
            if data.get('action') == 'answer':
                desc = RTCSessionDescription(data['sdp'], data['type'])
                await self.pc.setRemoteDescription(desc)
                break

    def toggle_ready(self):
        if self.channel:
            self.channel.send(json.dumps({'action': 'ready'}))

class RemotePeer(BasePeer):
    def __init__(self, username, code, window, loop):
        super().__init__(username, window, loop)
        self.code = code
        asyncio.create_task(self._setup())

    async def _setup(self):
        if not await self._connect_signaling():
            return
        await self.ws.send(json.dumps({'action': 'lookup', 'code': self.code, 'username': self.username}))
        self.window.show_status("Recherche de l'hôte...")

        async for msg in self.ws:
            print("Message reçu :", msg)
            data = json.loads(msg)
            if data.get('action') == 'found':
                self.window.show_remote_info(data.get('username'))
                self.window.enable_join()
            elif data.get('action') == 'offer':
                await self._handle_offer(data)
                break

    async def _handle_offer(self, data):
        offer = RTCSessionDescription(data['sdp'], data['type'])
        await self.pc.setRemoteDescription(offer)
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)
        await self.ws.send(json.dumps({'action': 'answer', 'sdp': self.pc.localDescription.sdp, 'type': self.pc.localDescription.type}))

        # Ajout des flux vidéo et audio
        @self.pc.on("track")
        async def on_track(track):
            if track.kind == "video":
                self.window.display_video(track)  # Implémentez display_video pour afficher le flux
            elif track.kind == "audio":
                self.window.play_audio(track)  # Implémentez play_audio pour jouer le son

        @self.pc.on("datachannel")
        def on_datachannel(channel):
            self.channel = channel
            input_handler = InputHandler(channel)  # Crée une instance d'InputHandler
            input_handler.start_capture()  # Démarre la capture des événements clavier et souris

        @self.pc.on("iceconnectionstatechange")
        def on_ice_connection_state_change():
            if self.pc.iceConnectionState == "failed":
                self.window.show_error("Échec de la connexion ICE.")
