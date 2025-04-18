# signaling_server.py
# WebSocket-based signaling for STUN/TURN negotiation and code exchange

import asyncio
import json
import websockets
import os
from http import HTTPStatus

PORT = 8765
# Use a dict to map registration codes to websocket connections
clients: dict[str, websockets.WebSocketServerProtocol] = {}

async def process_request(path, request_headers):
    """
    Vérifie que la méthode HTTP est GET pour les connexions WebSocket.
    Répond avec HTTP 200 pour les requêtes HEAD (health checks).
    Rejette toutes les autres méthodes (POST, PUT, etc.).
    """
    method = request_headers.get(":method", "GET")  # Vérifie la méthode HTTP
    if method == "HEAD":
        # Répondre avec HTTP 200 pour les requêtes HEAD (health checks)
        return HTTPStatus.OK, [("Content-Type", "text/plain")], b""
    elif method != "GET":
        # Rejeter toutes les autres méthodes non conformes
        print(f"Requête rejetée : méthode {method} non autorisée.")
        return HTTPStatus.METHOD_NOT_ALLOWED, [("Content-Type", "text/plain")], b"Method Not Allowed\n"

async def handler(websocket, path):
    try:
        async for msg in websocket:
            data = json.loads(msg)
            action = data.get('action')
            code = data.get('code')

            if action == 'register':
                clients[code] = websocket
                print(f"Host registered with code {code}")
            elif action == 'lookup':
                peer = clients.get(code)
                if peer:
                    # Notify remote
                    await websocket.send(json.dumps({'action': 'found', 'username': data.get('username')}))
                    # Notify host
                    await peer.send(json.dumps({'action': 'remote_found', 'username': data.get('username')}))
            else:
                # Relay all other messages (SDP/ICE, inputs)
                target = clients.get(code)
                if target and target.open:
                    await target.send(msg)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Clean up any registrations for this websocket
        to_remove = [key for key, ws in clients.items() if ws == websocket]
        for key in to_remove:
            del clients[key]

async def start():
    port = int(os.getenv("PORT", PORT))  # Render sets PORT automatically
    server = await websockets.serve(
        handler,
        "0.0.0.0",
        port,
        process_request=process_request
    )
    print(f"Signaling server started on port {port}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(start())
