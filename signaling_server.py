# signaling_server.py
# WebSocket-based signaling for STUN/TURN negotiation and code exchange

import asyncio
import json
import websockets
import os
from http import HTTPStatus
from websockets.server import Request  # ou websockets.asyncio.server.Request

PORT = 8765
# Use a dict to map registration codes to websocket connections
clients: dict[str, websockets.WebSocketServerProtocol] = {}

async def process_request(connection, request : Request):
    """
    Vérifie que la méthode HTTP est GET pour les connexions WebSocket.
    Répond avec HTTP 200 pour les requêtes HEAD (health checks).
    Rejette toutes les autres méthodes (POST, PUT, etc.).
    """
    if request.headers.get("Upgrade", "").lower() != "websocket":
        return (
            HTTPStatus.OK,
            [("Content-Type", "text/plain")],
            b"OK\n",
        )

    # Sinon, None → on continue normalement le handshake WebSocket
    return None


async def handler(websocket):
    print(websocket)
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
