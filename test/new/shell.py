import socket
import json
import sys

ROUTER_HOST = '127.0.0.1'

def send_command(command, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((ROUTER_HOST, port))
            
            # Send JSON command
            message = json.dumps({"command": command})
            client.sendall(message.encode())

            # Receive response
            response = client.recv(1024)
            response_data = json.loads(response.decode())

            # Accessing JSON fields
            if isinstance(response_data, dict):
                print("Response:", response_data)
                if "response" in response_data:
                    print("Response field:", response_data["response"])
                else:
                    print("No 'response' field found in JSON.")
            else:
                print("Invalid JSON received:", response_data)

    except ConnectionRefusedError:
        print("Daemon is down. Unable to connect.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <port>")
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port. Please enter a valid integer.")
        sys.exit(1)
    
    while True:
        cmd = input("Enter command (or type 'exit' to quit): ")
        if cmd.lower() == 'exit':
            print("Exiting shell...")
            break
        send_command(cmd, port)
