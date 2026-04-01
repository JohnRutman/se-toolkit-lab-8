import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:42002/ws/chat?access_key=nanokey"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"content": "What labs are available?"}))
        response = await ws.recv()
        print(response)

asyncio.run(main())
