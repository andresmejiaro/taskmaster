import socket
import os

SOCKET_PATH = "/tmp/daemon_socket"

# Ensure no leftover socket file exists
if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
server.listen(5)

print("Daemon is listening...")

while True:
    conn, _ = server.accept()
    data = conn.recv(1024)
    if data:
        print(f"Received: {data.decode()}")
        conn.sendall(b"ACK")  # Send response
    conn.close()

