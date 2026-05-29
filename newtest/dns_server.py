import socket
import threading
import dns.message
import dns.query as dq

from flask import Flask, render_template
from flask_socketio import SocketIO

from database import init_db, log_request
from enricher import resolve_true_sovereignty

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 53


@app.route("/")
def index():
    return render_template("index.html")


def dns_loop():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((LISTEN_IP, LISTEN_PORT))

    print(f"📡 DNS running on {LISTEN_PORT}", flush=True)

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            query = dns.message.from_wire(data)

            if not query.question:
                continue

            domain = query.question[0].name.to_text().rstrip(".")

            response = dq.udp(query, "8.8.8.8", timeout=2.0)
            sock.sendto(response.to_wire(), addr)

            # Process in a separate thread to avoid blocking the DNS loop
            # especially if enrichment causes more DNS lookups (circular dependency)
            threading.Thread(
                target=process, 
                args=(domain, addr[0], response), 
                daemon=True
            ).start()

        except Exception as e:
            print("DNS ERROR:", repr(e), flush=True)


def process(domain, client_ip, response):
    try:
        if "ip-api.com" in domain:
            return

        log_request(client_ip, domain)

        ip = None
        for a in response.answer:
            if a.rdtype == 1:
                ip = a[0].to_text()
                break

        if not ip:
            return

        telemetry = resolve_true_sovereignty(domain, ip)

        # 🔥 enforce safe structure for frontend
        t = telemetry if telemetry else {}
        event = {
            "domain": domain,
            "ip": ip,
            "lat": t.get("lat", 0),
            "lon": t.get("lon", 0),
            "country": t.get("country", "unknown"),
            "country_code": t.get("country_code", "UN"),
            "asn_owner": t.get("asn_owner", "unknown"),
            "true_sovereignty": t.get("true_sovereignty", "unknown"),
            "provider_group": t.get("provider_group", "Local / Independent"),
            "city": t.get("city", ""),
        }

        print("EMIT:", event, flush=True)

        socketio.emit("dns_event", event)

    except Exception as e:
        print("PROCESS ERROR:", repr(e), flush=True)


if __name__ == "__main__":
    init_db()

    threading.Thread(target=dns_loop, daemon=True).start()

    socketio.run(
        app,
        host="0.0.0.0",
        port=8081,
        debug=False,
        allow_unsafe_werkzeug=True
    )
