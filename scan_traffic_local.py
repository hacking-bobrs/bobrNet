import re
import socket

import urlextract
from scan_transmitter import send
from scapy.all import sniff, TCP, Raw

ext = urlextract.URLExtract()

def extract_domain(packet):
    """Analyzes packets to extract clean, valid accessed domains for ANY TLD."""
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        payload = packet[Raw].load.decode('utf-8', errors='ignore')
        l = ext.find_urls(payload)
        return l[0] if l else None
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