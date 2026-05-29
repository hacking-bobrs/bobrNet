import socket


def send(url: str, host: str = '127.0.0.1', port: int = 65432):
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
            if url is not None:
                client_socket.sendall(url.encode('utf-8'))

                #print(f"Successfully sent: '{message}' to {host}:{port}")

    except ConnectionRefusedError:
        print(f"Error: Could not connect to {host}:{port}. Is the receiver program running?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")