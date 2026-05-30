import socket


def send(url: str, host: str = '127.0.0.1', port: int = 65432):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

            client_socket.connect((host, port))

            if url is not None:
                client_socket.sendall(url.encode('utf-8'))

                #print(f"Successfully sent: '{message}' to {host}:{port}")

    except ConnectionRefusedError:
        print(f"Error: Could not connect to {host}:{port}. Is the receiver program running?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")