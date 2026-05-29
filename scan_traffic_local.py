import re
import socket

from scan_transmitter import send
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

    send(domain)






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