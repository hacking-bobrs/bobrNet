import socket
import threading
import signal
import sys
import dns.message
import dns.query

from DatabaseConnection import DatabaseConnection
from enricher import resolve_true_sovereignty

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 53

def dns_server():
    dns_loop()


def dns_loop():
    database = DatabaseConnection()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((LISTEN_IP, LISTEN_PORT))

    running = True

    def handle_docker_shutdown(signum, frame):
        nonlocal running
        print(f"Received signal ({signum}). Initiating graceful shutdown", flush=True)
        running = False

        print("Shutting down resources", flush=True)
        try:
            database.closeConnection()
            sock.close()
        except Exception as e:
            print(f"Error during cleanup: {e}", flush=True)
        finally:
            print("Exiting process.", flush=True)
            sys.exit(0)

    signal.signal(signal.SIGINT, handle_docker_shutdown)
    signal.signal(signal.SIGTERM, handle_docker_shutdown)

    print(f"📡 DNS running on {LISTEN_PORT}", flush=True)

    while running:
        try:
            data, addr = sock.recvfrom(65535)
            query = dns.message.from_wire(data)

            if not query.question:
                continue

            domain = query.question[0].name.to_text().rstrip(".")

            response = query.udp(query, "8.8.8.8", timeout=2.0)
            sock.sendto(response.to_wire(), addr)

            threading.Thread(
                target=process,
                args=(domain, addr[0], response, database),
                daemon=True
            ).start()

        except Exception as e:
            print("DNS ERROR:", repr(e), flush=True)


def process(domain, client_ip, response, database: DatabaseConnection):
    try:
        log_request(client_ip, domain)

        ip = None
        for a in response.answer:
            if a.rdtype == 1:
                ip = a[0].to_text()
                break

        if not ip:
            return

        telementry = resolve_true_sovereignty(domain, ip, database)

        print(telementry)

    except Exception as e:
        print("PROCESS ERROR:", repr(e), flush=True)