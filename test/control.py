import socket

SOCKET_PATH = "/tmp/daemon_socket"

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(SOCKET_PATH)
client.sendall(b"Hello from control program")
response = client.recv(1024)
print(f"Response from daemon: {response.decode()}")
client.close()

