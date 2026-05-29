from threading import Thread

import requests
import socket
from flask import Flask, render_template
from flask_socketio import SocketIO
from datetime import datetime, time
from bobr_db import save_to_db, init_db, get_chronological_traffic_log
from scan_domains_local import run_scanner

# Define the server address and port
HOST = '127.0.0.1'  # Localhost (same computer)
PORT = 65432        # Arbitrary non-privileged port

geo_cache = {}

def get_geo_location(domain):
    """Resolves a domain to an IP and fetches its geographical coordinates."""
    if domain in geo_cache:
        return geo_cache[domain]

    try:
        # Resolve domain to IP address
        ip_address = socket.gethostbyname(domain)

        # Use ip-api (Free for development, rate limit: 45 requests/min)
        response = requests.get(f"http://ip-api.com/json/{ip_address}").json()

        if response.get("status") == "success":
            # --- MODIFIED HERE ---
            # Store the raw JSON API response directly
            geo_info = response
            # Explicitly ensure the resolved IP address is included (or use response.get('query'))
            geo_info["resolved_ip"] = ip_address

            geo_cache[domain] = geo_info
            return geo_info
    except Exception as e:
        # Handle lookup or connection errors gracefully
        pass

    return None

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

@app.route("/")
def index():
    return render_template("index.html")


def send_geo_to_socket(domain, geo_info):
    """
    Formatures and emits the geo data over Socket.IO to match the 
    frontend 'dns_event' listener requirements.
    """
    if not geo_info:
        return

    

    # Structure the payload to mirror what your JS front-end expects:
    # data.country, data.provider_group, etc.
    true_sovereignty = geo_info.get("country") # default
    
    cdn_keywords = ["CLOUDFLARE", "AKAMAI", "AMAZON", "FASTLY", "GOOGLE", "MICROSOFT"]
    if any(keyword in geo_info.get("as").upper() for keyword in cdn_keywords):
        # For a pure tech demo, you can flag these as structurally US-controlled
        # due to Cloud Act jurisdictions, regardless of where the local node lives.
        true_sovereignty = "United States (US Cloud Act Jurisdiction)"
    payload = {
        "domain": domain,
        "ip": geo_info.get("query"),           # ip-api keeps the IP inside the 'query' field
        "country": geo_info.get("country") or "Unknown",
        "city": geo_info.get("city") or "Unknown",
        "lat": geo_info.get("lat"),
        "lon": geo_info.get("lon"),
        "asn_owner": geo_info.get("as") or "Unknown",
        "provider_group": geo_info.get("isp") or "Unknown", # mapping ISP to provider_group
        "true_sovereignty": true_sovereignty,
        "timestamp": datetime.now().strftime('%H:%M:%S')
    }

    try:
        # Emit the event! Your JS code listens for "dns_event"
        socketio.emit("dns_event", payload)
        print(f"[➔] Broadcasted {domain} mapping over Socket.IO")
    except Exception as e:
        print(f"[!] Failed to emit socket event: {e}")


@socketio.on('connect')
def handle_connect():
    print(f"[+] Frontend connected")
    for (d,gi) in get_chronological_traffic_log():
                send_geo_to_socket(d, gi)
                print(f"[History] Sent cached domain {d} to frontend.")

def run_domain_processor():
    init_db()  # Ensure the database and tables are initialized before processing any domains
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Allow the socket to reuse the address (prevents "Address already in use" errors)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Domain Processor is listening on {HOST}:{PORT}...")
        print("Press Ctrl+C to stop the server.")

        try:
            
            
            
            


            while True:
                # Wait and accept an incoming connection from the sender function
                conn, addr = server_socket.accept()
                
                # Handle the connected client
                with conn:
                    # Loop to read all data from this specific connection
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            # No more data from this connection
                            break
                        
                        message = data.decode('utf-8')
                        if message != "ip-api.com":
                            #print(f"[{addr[0]}:{addr[1]}] Received: {message}")
                            geo_info = get_geo_location(message)
                            if geo_info:
                                save_to_db(message, geo_info)
                                send_geo_to_socket(message, geo_info)

        except KeyboardInterrupt:
            print("\nDomain Processor shutting down gracefully.")

if __name__ == "__main__":
    Thread(target=run_scanner).start()
    Thread(target=run_domain_processor).start()

    socketio.run(
        app,
        host="0.0.0.0",
        port=8081,
        debug=False,
        allow_unsafe_werkzeug=True
    )
    





