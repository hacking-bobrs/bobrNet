from fastapi import FastAPI, WebSocket
import asyncio
import json
from DatabaseConnection import DatabaseConnection
from contextlib import asynccontextmanager


class Server:
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

        self.register_routes()

    def shutdown(self):
        self.database.closeConnection()

    def register_routes(self):
        @self.app.post("/fetch")
        async def fetch_data():
            return {
                "type": "fetch",
                "data": self.database.getBigData()
            }

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