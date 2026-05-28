import socket, dns.query as dq
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 53))
while True:
    msg = dq.receive_udp(sock)
    for a in msg.sections:
        for b in a:
            print(b.to_styled_text())
    resp = dq.udp(msg[0], "8.8.8.8")
    dq.send_udp(sock, resp, msg[2])