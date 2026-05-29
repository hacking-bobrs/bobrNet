from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from DatabaseConnection import DatabaseConnection
from contextlib import asynccontextmanager


class Server:

    MOCK_DATA = [
        {
            "domain": "google.com",
            "ip": "172.217.16.142",
            "lat": 37.0902,
            "lon": -95.7129,
            "country": "United States",
            "country_code": "US",
            "provider_group": "Google Cloud",
            "asn_owner": "AS15169 Google LLC"
        },
        {
            "domain": "bobrnet.org",
            "ip": "198.51.100.42",
            "lat": 51.9194,
            "lon": 19.1451,
            "country": "Poland",
            "country_code": "PL",
            "provider_group": "Cloudflare",
            "asn_owner": "AS13335 Cloudflare, Inc."
        },
        {
            "domain": "github.com",
            "ip": "140.82.121.4",
            "lat": 51.1657,
            "lon": 10.4515,
            "country": "Germany",
            "country_code": "DE",
            "provider_group": "AWS",
            "asn_owner": "AS16509 Amazon.com, Inc."
        },
        {
            "domain": "wikipedia.org",
            "ip": "103.102.166.224",
            "lat": 36.2048,
            "lon": 138.2529,
            "country": "Japan",
            "country_code": "JP",
            "provider_group": "DigitalOcean",
            "asn_owner": "AS141030 DigitalOcean, LLC"
        },
        {
            "domain": "aws.amazon.com",
            "ip": "52.95.26.47",
            "lat": -14.2350,
            "lon": -51.9253,
            "country": "Brazil",
            "country_code": "BR",
            "provider_group": "AWS",
            "asn_owner": "AS16509 Amazon.com, Inc."
        }
    ]

    def __init__(self):
        print("Initializing server")

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            sync_task = asyncio.create_task(self.sync_loop())
            yield

            sync_task.cancel()
            try:
                await sync_task
            except asyncio.CancelledError:
                pass

            self.shutdown()

        self.app = FastAPI(lifespan=lifespan)
        self.clients = set()
        self.database = DatabaseConnection()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:8082"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.register_routes()

    def shutdown(self):
        self.database.closeConnection()

    def register_routes(self):
        @self.app.get("/fetch")
        async def fetch_data():
            return self.MOCK_DATA

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.clients.add(websocket)
            print("Client connected via WebSocket")

            try:
                while True:
                    await websocket.receive_text()
            except Exception:
                pass
            finally:
                self.clients.remove(websocket)
                print("Client disconnected from WebSocket")

    async def sync_loop(self):
        while True:
            newData = self.database.getBigData()

            if self.clients and self.data:
                packet = {
                    "type": "sync",
                    "data": newData
                }

                payload = json.dumps(packet)

                active_clients = list(self.clients)

                for client in active_clients:
                    try:
                        await client.send_text(payload)
                    except Exception:
                        self.clients.discard(client)

            await asyncio.sleep(1) # Broadcast rate (1 Update per Second)