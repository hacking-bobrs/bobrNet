import socket, dns.query as dq
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 50_000))
while True:
    msg = dq.receive_udp(sock)
    print(msg)
    resp = dq.udp(msg[0], "8.8.8.8")
    dq.send_udp(sock, resp, msg[2])