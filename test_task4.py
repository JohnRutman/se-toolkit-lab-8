import asyncio
import json
import websockets

async def test_what_went_wrong():
    uri = "ws://localhost:42002/ws/chat?access_key=nanokey"
    async with websockets.connect(uri) as ws:
        # First trigger a request that will fail
        await ws.send(json.dumps({"content": "What labs are available?"}))
        response1 = await ws.recv()
        print("Response 1:", response1[:200])
        
        # Wait a bit for logs to propagate
        await asyncio.sleep(5)
        
        # Now ask what went wrong
        await ws.send(json.dumps({"content": "What went wrong?"}))
        response2 = await ws.recv()
        print("Response 2:", response2)

asyncio.run(test_what_went_wrong())
