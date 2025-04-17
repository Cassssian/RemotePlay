# signaling_server.py
# WebSocket-based signaling for STUN/TURN negotiation and code exchange

import asyncio, json, websockets, os

PORT = 10000
clients = set()

async def handler(websocket, path):
    clients.add(websocket)
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
    except:
        pass
    finally:
        clients.remove(websocket)

async def start():
    port = int(os.getenv("PORT", 8765))  # Render définit automatiquement la variable PORT
    server = await websockets.serve(handler, "0.0.0.0", port)
    print(f"Serveur de signalisation démarré sur le port {port}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(start())
