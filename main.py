from threading import Thread
import keyboard
import requests
import socket
import tomllib
from flask import Flask, render_template
from flask_socketio import SocketIO
from datetime import datetime
from database import save_to_db, init_db, get_chronological_traffic_log
import scan_traffic_dns
import scan_traffic_local

with open("bobrnet.config.toml", "rb") as f:
    config = tomllib.load(f)


HOST = '127.0.0.1'  
PORT = 65432        # Arbitrary non-privileged port

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

geo_cache = {}

def get_geo_location(domain):
    """Resolves a domain to an IP and fetches its geographical coordinates."""
    if domain in geo_cache:
        return geo_cache[domain]

    try:
        ip_address = socket.gethostbyname(domain)

        response = requests.get(f"http://ip-api.com/json/{ip_address}").json()

        if response.get("status") == "success":
            geo_info = response
            geo_info["resolved_ip"] = ip_address

            geo_cache[domain] = geo_info
            return geo_info
    except Exception as e:
        pass

    return None


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

    
    true_sovereignty = geo_info.get("country")
    
    cdn_keywords = ["CLOUDFLARE", "AKAMAI", "AMAZON", "FASTLY", "GOOGLE", "MICROSOFT"]
    if any(keyword in geo_info.get("as").upper() for keyword in cdn_keywords):
        true_sovereignty = "United States (US Cloud Act Jurisdiction)"
    payload = {
        "domain": domain,
        "ip": geo_info.get("query"),          
        "country": geo_info.get("country") or "Unknown",
        "country_code": geo_info.get("countryCode") or "UN",
        "city": geo_info.get("city") or "Unknown",
        "lat": geo_info.get("lat"),
        "lon": geo_info.get("lon"),
        "asn_owner": geo_info.get("as") or "Unknown",
        "provider_group": geo_info.get("isp") or "Unknown", 
        "true_sovereignty": true_sovereignty,
        "timestamp": datetime.now().strftime('%H:%M:%S')
    }

    try:
        socketio.emit("dns_event", payload)
        print(f"[➔] Broadcasted {domain} mapping over Socket.IO")
    except Exception as e:
        print(f"[!] Failed to emit socket event: {e}")


@socketio.on('connect')
def handle_connect():
    print(f"[+] Frontend connected")
    #for (d,gi) in get_chronological_traffic_log():
    #            send_geo_to_socket(d, gi)
                #print(f"[History] Sent cached domain {d} to frontend.")

def run_domain_processor():
    init_db()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Domain Processor is listening on {HOST}:{PORT}...")
        print("Press Ctrl+C to stop the server.")

        try:
            while True:
                conn, addr = server_socket.accept()
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        message = data.decode('utf-8')
                        if message not in ["ip-api.com", "a.basemaps.cartocdn.com", "b.basemaps.cartocdn.com", "c.basemaps.cartocdn.com"]:
                            print(f"[{addr[0]}:{addr[1]}] Received: {message}")
                            geo_info = get_geo_location(message)
                            if geo_info:
                                save_to_db(message, geo_info)
                                send_geo_to_socket(message, geo_info)

        except KeyboardInterrupt:
            print("\nDomain Processor shutting down.")

def await_keyboard_input():
    
    while True:
        event = keyboard.read_event()
        
        if event.event_type == keyboard.KEY_DOWN and event.name == 'ü':
            print(f"\nErfolgreich erkannt! Du hast die Taste '{event.name}' gedrückt.")
            for (d,gi) in get_chronological_traffic_log():
                send_geo_to_socket(d, gi)
            

if __name__ == "__main__":
    analysis_mode = config.get("analysis", {}).get("mode", "sniffing")
    if analysis_mode == "sniffing":
        scanner = scan_traffic_local.run_scanner
    else:
        scanner = scan_traffic_dns.run_scanner
    print(f"[*] Starting in '{analysis_mode}' mode.")
    Thread(target=scanner).start()
    Thread(target=run_domain_processor).start()
    Thread(target=await_keyboard_input).start()

    socketio.run(
        app,
        host="0.0.0.0",
        port=8081,
        debug=False,
        allow_unsafe_werkzeug=True
    )
    
