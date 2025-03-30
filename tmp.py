#!/bin/python
import socket
import json
import sys

def send_command(command, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((ROUTER_HOST, port))
            message = json.dumps({"command": command})
            client.sendall(message.encode())
            response = client.recv(1024)
    except ConnectionRefusedError:
        print("Daemon is down. Unable to connect.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
