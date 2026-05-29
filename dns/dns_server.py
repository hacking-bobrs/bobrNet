import socket
import dns.query as dq

def dns_server():
    # Listen on all available network interfaces on port 53 (Standard DNS port)
    # Note: Ports below 1024 usually require Administrator/sudo privileges
    LISTEN_IP = "0.0.0.0"
    LISTEN_PORT = 53

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))

    print(f"Custom DNS Server listening on {LISTEN_IP}:{LISTEN_PORT}...")

    while True:
        try:
            # 1. Receive the DNS query from your Pixel phone
            # receive_udp returns a tuple: (dns_message, background_context)
            query_msg, context = dq.receive_udp(sock)
            client_address = context.client_address

            print(f"Received query from {client_address}")

            # 2. Forward the exact same query to Google DNS
            # udp() sends the query and automatically waits for the response
            response_msg = dq.udp(query_msg, "8.8.8.8", timeout=3.0)

            # 3. Send Google's response back to your Pixel phone
            dq.send_udp(sock, response_msg, client_address)
            print(f"Successfully forwarded response to {client_address}")

        except Exception as e:
            print(f"Error handling request: {e}")
