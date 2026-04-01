import asyncio
import json
import websockets

async def create_health_check():
    uri = "ws://localhost:42002/ws/chat?access_key=nanokey"
    async with websockets.connect(uri) as ws:
        # Create health check cron job
        await ws.send(json.dumps({"content": "Create a health check for this chat that runs every 2 minutes using your cron tool. Each run should check for LMS/backend errors in the last 2 minutes, inspect a trace if needed, and post a short summary here. If there are no recent errors, say the system looks healthy."}))
        response1 = await ws.recv()
        print("Create cron:", response1[:300])
        
        await asyncio.sleep(3)
        
        # List scheduled jobs
        await ws.send(json.dumps({"content": "List scheduled jobs."}))
        response2 = await ws.recv()
        print("List jobs:", response2[:300])

asyncio.run(create_health_check())
