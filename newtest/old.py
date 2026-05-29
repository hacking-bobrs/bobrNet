import socket
import threading
import dns.message
import dns.query as dq
from flask import Flask, render_template
from flask_socketio import SocketIO
from database import init_db, log_request
from enricher import resolve_true_sovereignty

# Initialize Web App & WebSockets
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 5353

@app.route('/')
def index():
    return render_template('index.html') # The map frontend layout

# Core DNS Interception Loop running inside a background thread
def run_dns_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    print(f"📡 DNS Engine listening on port {LISTEN_PORT}...", flush=True)

    while True:
        try:
            data, client_address = sock.recvfrom(65535)
            query_msg = dns.message.from_wire(data)

            if query_msg.question:
                dns_question = query_msg.question[0]
                requested_domain = dns_question.name.to_text().rstrip('.')
                
                # 1. Forward directly to Google to prevent phone latency
                print("replying to:", client_address, flush=True)

                response_msg = dq.udp(query_msg, "8.8.8.8", timeout=3.0)
                sock.sendto(response_msg.to_wire(), client_address)

                # 2. Spin off telemetry processing asynchronously so DNS stays fast
                threading.Thread(target=process_telemetry, args=(client_address[0], requested_domain, response_msg)).start()

        except Exception as e:
            print(f"DNS Loop Error: {e}", flush=True)

def process_telemetry(client_ip, domain, response_msg):
    # Log the raw footprint request to SQLite
    log_request(client_ip, domain)

    # Extract the resolved destination IP from the DNS answer records
    target_ip = None
    for answer in response_msg.answer:
        if answer.rdtype == 1: # IPv4 A Record
            target_ip = answer[0].to_text()
            break

    if target_ip:
        # Run our sophisticated country/ASN mapping
        telemetry = resolve_true_sovereignty(domain, target_ip)
        if telemetry:
            print(f"📱 [STREAM] {domain} -> {telemetry['true_sovereignty']} ({telemetry['asn_owner']})", flush=True)
            # 🚀 Push the data instantly to the browser map via WebSockets!
            socketio.emit('new_dns_query', telemetry)

if __name__ == '__main__':
    init_db() # Run SQL setups
    
    # Start the DNS core thread
    dns_thread = threading.Thread(target=run_dns_server, daemon=True)
    dns_thread.start()
    
    # Start the Dashboard Web Interface on port 8080
    socketio.run(app, host='0.0.0.0', port=8081)
