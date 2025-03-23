import socket
import sys
import json

HOST = '127.0.0.1'

def setup_server(port):
    """Initialize and return a configured server socket."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Free the port instantly on exit
    server.bind((HOST, port))
    server.listen()
    print(f"Listening on {HOST}:{port}...")
    return server

def process_command(data):
    """Process the received command and return a response."""
    try:
        response_data = json.loads(data.decode())
        print("Debug: --------------------------------------")
        if isinstance(response_data, dict) and "command" in response_data:
            print("command:", response_data["command"])
            if response_data["command"] == "start":
                print("starting...")
                status, message = "success", "Daemon started"
            else:
                status, message = "error", "Unknown command"
        else:
            print("Invalid JSON received:", response_data)
            status, message = "error", "Invalid JSON format"
        print("Debug: --------------------------------------")
    except json.JSONDecodeError:
        status, message = "error", "Malformed JSON"
    
    return json.dumps({"status": status, "message": message}).encode()

def handle_client(conn, addr):
    """Handle incoming client connection."""
    print(f"Connected by {addr}")
    try:
        data = conn.recv(1024)
        if data:
            response = process_command(data)
            conn.sendall(response)
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()

def start_daemon(port):
    """Start the daemon server and handle incoming connections."""
    server = setup_server(port)
    try:
        while True:
            conn, addr = server.accept()
            handle_client(conn, addr)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.close()

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
