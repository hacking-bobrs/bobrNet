import socket, dns.query as dq
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 50_000))
while True:
    msg = dq.receive_udp(sock)
    print(msg)
    dq.send_udp(sock, msg, ("8.8.8.8", 53))