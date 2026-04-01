import asyncio
import json
import websockets

async def test():
    uri = "ws://localhost:42002/ws/chat?access_key=nanokey"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"content": "Any LMS errors in 10 min?"}))
        response = await ws.recv()
        print(response[:200])

asyncio.run(test())
