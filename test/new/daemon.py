import socket
import sys
import json

HOST = '127.0.0.1'

def start_daemon(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Free the port instantly on exit
            server.bind((HOST, port))
            server.listen()
            print(f"Listening on {HOST}:{port}...")
            
            while True:
                conn, addr = server.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if data:
                        response_data = json.loads(data.decode())
                        if isinstance(response_data, dict):
                            if "command" in response_data:
                                print("Response field:", response_data["command"])
                            else:
                                print("No 'response' field found in JSON.")
                        else:
                            print("Invalid JSON received:", response_data)

                    conn.sendall(b'{"status": "ok"}')

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <port>")
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port. Please enter a valid integer.")
        sys.exit(1)
    
    start_daemon(port)
