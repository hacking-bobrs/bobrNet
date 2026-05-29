import re
import socket

from scapy.all import sniff, TCP, Raw


def extract_domain(packet):
    """Analyzes packets to extract clean, valid accessed domains for ANY TLD."""
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        payload = packet[Raw].load.decode('utf-8', errors='ignore')

        # 1. Look for standard HTTP GET/POST Requests
        if "Host:" in payload:
            for line in payload.split("\r\n"):
                if line.startswith("Host:"):
                    return line.split(" ")[1].strip()

        # 2. Look for HTTPS (SNI) with a universal TLD Regex
        elif packet[TCP].dport == 443:
            match = re.search(r'\b([a-zA-Z0-9][-a-zA-Z0-9]*\.)+[a-zA-Z]{2,24}\b', payload)
            if match:
                domain = match.group(0).lower()

                if not domain.startswith('.') and not domain.endswith('.'):
                    return domain

    return None


def process_packet(packet):
    """Callback function for every captured packet."""
    domain = extract_domain(packet)

    send_string_to_receiver(domain)


def send_string_to_receiver(message: str, host: str = '127.0.0.1', port: int = 65432):
    """
    Sends a string message to a listening socket server.

    :param message: The string data you want to send.
    :param host: The IP address of the receiver (default is localhost).
    :param port: The port number the receiver is listening on.
    """
    try:
        # 1. Create a TCP/IP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

            # 2. Connect to the receiver
            client_socket.connect((host, port))

            # 3. Convert the string to bytes (UTF-8) and send it
            if message is not None:
                client_socket.sendall(message.encode('utf-8'))

                #print(f"Successfully sent: '{message}' to {host}:{port}")

    except ConnectionRefusedError:
        print(f"Error: Could not connect to {host}:{port}. Is the receiver program running?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")




def run_scanner():
    print("[*] Starting Network Sniffer... Press Ctrl+C to stop.")
    print("[*] Note: This script requires root/administrator privileges.")

    try:
        sniff(filter="tcp", prn=process_packet, store=0)
    except KeyboardInterrupt:
        print("\n[*] Stopping sniffer. Safe travels!")
    except PermissionError:
        print("\n[!] Error: You must run this script with sudo/administrator privileges.")


if __name__ == "__main__":
    run_scanner()