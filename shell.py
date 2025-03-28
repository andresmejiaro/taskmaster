#!/bin/python
import socket
import json
import sys
import readline
import os

ROUTER_HOST = '127.0.0.1'
PROMPT = "\033[92mtaskmaster> \033[0m"
COLOR_ERROR = "\033[91m"
COLOR_OK = "\033[94m"
COLOR_RESET = "\033[0m"
HISTORY_FILE = os.path.expanduser("~/.taskmaster_history")

def init_readline():
    """Initialize readline for line editing, history, and completion."""
    readline.parse_and_bind("tab: complete")
    try:
        readline.read_history_file(HISTORY_FILE)
    except FileNotFoundError:
        pass

def save_history():
    """Save the current session's command history to a file."""
    try:
        readline.write_history_file(HISTORY_FILE)
    except Exception as e:
        print(f"Could not save history: {e}")

def send_command(command, port):
    """Send a JSON command to the daemon and process the response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((ROUTER_HOST, port))
            # Build and send JSON command message
            message = json.dumps({"command": command})
            client.sendall(message.encode())

            # Receive and process the response
            response = client.recv(1024)
            process_response(response)
    except ConnectionRefusedError:
        print("Daemon is down. Unable to connect.")
    except Exception as e:
        print("An error occurred:", e)

def process_response(response):
    """Process and print the JSON response from the daemon."""
    try:
        response_data = json.loads(response.decode())
    except json.JSONDecodeError:
        print("Invalid JSON received:", response)
        return

    if isinstance(response_data, dict):
        print("Response:", response_data)
        if "status" in response_data and "message" in response_data:
            status = response_data["status"]
            message = response_data["message"]
            if status == "error":
                print(f"{COLOR_ERROR}[ERROR]: {message}{COLOR_RESET}")
            else:
                print(f"{COLOR_OK}{message}{COLOR_RESET}")
        else:
            print("Missing 'status' or 'message' in response JSON.")
    else:
        print("Invalid JSON format received:", response_data)

def get_command():
    """Prompt the user for a command and return it."""
    try:
        return input(PROMPT)
    except EOFError:
        print("\nInput error or connection closed unexpectedly. Exiting.")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <port>")
        sys.exit(1)
    
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port. Please enter a valid integer.")
        sys.exit(1)
    
    init_readline()
    
    try:
        while True:
            cmd = get_command()
            if cmd.lower() == 'exit':
                print("Exiting shell...")
                break
            if cmd.strip():  # Only send non-empty commands
                send_command(cmd, port)
    finally:
        save_history()

if __name__ == "__main__":
    main()
