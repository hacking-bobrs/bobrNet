import socket
import threading
import dns.message
import dns.query

from scan_transmitter import send

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 53
UPSTREAM_DNS = "8.8.8.8"

def handle_dns_query(data, addr, sock):
    try:
        query = dns.message.from_wire(data)

        if not query.question:
            return

        domain = query.question[0].name.to_text().rstrip(".")
        send(domain)

        response = dns.query.udp(query, UPSTREAM_DNS, timeout=2.0)
        sock.sendto(response.to_wire(), addr)

    except Exception as e:
        print(f"Error handling query from {addr[0]}: {repr(e)}", flush=True)

def run_scanner():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((LISTEN_IP, LISTEN_PORT))
        print(f"DNS Server running on {LISTEN_IP}:{LISTEN_PORT}", flush=True)
        print(f"Forwarding upstream queries to {UPSTREAM_DNS}\n" + "-"*50, flush=True)
    except PermissionError:
        print(f"Error: Port {LISTEN_PORT} requires administrative privileges. Run CMD/PowerShell as Administrator.", flush=True)
        return
    except Exception as e:
        print(f"Failed to bind to port {LISTEN_PORT}: {e}", flush=True)
        return

    while True:
        try:
            data, addr = sock.recvfrom(65535)
            threading.Thread(
                target=handle_dns_query, 
                args=(data, addr, sock), 
                daemon=True
            ).start()
        except Exception as e:
            print("DNS Loop Error:", repr(e), flush=True)
