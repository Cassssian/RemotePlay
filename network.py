# network.py
# Peer classes for host and remote: manage signaling and WebRTC

import asyncio
import json
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription
from utils import generate_access_code
from streaming import ScreenTrack, AudioTrack  # Import des flux vidéo et audio

SIGNALING_URL = 'ws://127.0.0.1:8765'

class BasePeer:
    def __init__(self, username, window, loop):
        self.username = username
        self.window = window
        self.loop = loop
        self.pc = RTCPeerConnection(configuration={
            "iceServers": [
                {"urls": "stun:stun.l.google.com:19302"},  # Serveur STUN public
                {"urls": "turn:turn.bistri.com:80", "username" : "homeo", "credential" : "homeo"}  # Autre serveur STUN public
            ]
        })
        self.channel = None

    async def _connect_signaling(self):
        try:
            self.ws = await websockets.connect(SIGNALING_URL)
            return True
        except Exception as e:
            self.window.show_error(f"Impossible de joindre le signaling server : {e}")
            return False

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
            print("mess recu" , msg)
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
                self.window.display_video(track)
            elif track.kind == "audio":
                self.window.play_audio(track)

        @self.pc.on("iceconnectionstatechange")
        def on_ice_connection_state_change():
            if self.pc.iceConnectionState == "failed":
                self.window.show_error("Échec de la connexion ICE.")
