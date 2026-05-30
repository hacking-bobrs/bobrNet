import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK
from scan_transmitter import send
from urllib.parse import urlsplit

async def handler(websocket):
    async for message in websocket:
        print("Received from websocket:", message)
        # TODO sanitize url
        cleaned_url = urlsplit(message).hostname
        send(cleaned_url)

async def main():
    async with serve(handler, "", 24096) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
