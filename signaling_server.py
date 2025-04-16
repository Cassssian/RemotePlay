# signaling_server.py
# WebSocket-based signaling for STUN/TURN negotiation and code exchange

import asyncio, json, websockets

PORT = 8765
clients = {}

async def handler(websocket):
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

async def start():
    server = await websockets.serve(handler, '0.0.0.0', PORT)
    print(f"Signaling server listening on {PORT}")
    return server
