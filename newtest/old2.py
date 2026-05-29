import socket
import dns.message
import dns.query as dq

from flask import Flask, render_template
from flask_socketio import SocketIO

from database import init_db, log_request
from enricher import resolve_true_sovereignty

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 5353

app = Flask(__name__)

# IMPORTANT: force threading mode, avoid eventlet interference
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)


@app.route("/")
def index():
    return render_template("index.html")


def run_dns_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # important for Docker + restarts
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((LISTEN_IP, LISTEN_PORT))

    print(f"📡 DNS Engine listening on port {LISTEN_PORT}...", flush=True)

    while True:
        try:
            data, client_address = sock.recvfrom(65535)

            query_msg = dns.message.from_wire(data)
            if not query_msg.question:
                continue

            dns_question = query_msg.question[0]
            domain = dns_question.name.to_text().rstrip(".")

            print(f"📥 query: {domain} from {client_address}", flush=True)

            # forward upstream
            response_msg = dq.udp(query_msg, "8.8.8.8", timeout=3.0)

            # respond back to client
            sock.sendto(response_msg.to_wire(), client_address)

            print(f"📤 responded to {client_address}", flush=True)

            # async telemetry (safe under flask-socketio threading mode)
            socketio.start_background_task(
                process_telemetry,
                client_address[0],
                domain,
                response_msg
            )

        except Exception as e:
            print(f"DNS Loop Error: {repr(e)}", flush=True)


def process_telemetry(client_ip, domain, response_msg):
    try:
        log_request(client_ip, domain)

        target_ip = None
        for ans in response_msg.answer:
            if ans.rdtype == 1:  # A record
                target_ip = ans[0].to_text()
                break

        if not target_ip:
            return

        telemetry = resolve_true_sovereignty(domain, target_ip)
        if telemetry:
            print(
                f"📱 {domain} -> {telemetry['true_sovereignty']} ({telemetry['asn_owner']})",
                flush=True
            )
            socketio.emit("new_dns_query", telemetry)

    except Exception as e:
        print(f"Telemetry error: {repr(e)}", flush=True)


if __name__ == "__main__":
    init_db()

    # start DNS server in background (socketio-safe way)
    socketio.start_background_task(run_dns_server)

    socketio.run(
        app,
        host="0.0.0.0",
        port=8081,
        debug=False,
        allow_unsafe_werkzeug=False
    )
