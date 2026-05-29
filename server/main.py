import uvicorn
import signal
import sys
from Server import Server

if __name__ == '__main__':
    try:
        server = Server()

        print("Starting server")
        uvicorn.run(
            server.app,
            host="0.0.0.0",
            port=8000,
            reload=False
        )

    except Exception as error:
        print(f"Error while running server: {error}")
