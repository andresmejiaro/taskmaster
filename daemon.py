#!/bin/python
import socket
import sys
import json
from ManagedProcess import ManagedProcess

HOST = '127.0.0.1'

class TaskMaster:
    def __init__(self):
        self.updateParsing()
        # Launch all processes at initialization
        for proc in self.processes.values():
            proc.launchProcess()

    def parseJson(self, route):
        with open(route, "r") as file:
            return json.load(file)

    def updateParsing(self):
        outJson = self.parseJson("conf.json")
        self.processes = {key: ManagedProcess(value) for key, value in outJson.items()}

    def updateProcesses(self):
        for proc in self.processes.values():
            proc.launchProcess()

    def checkStatus(self):
        status_report = {key: proc.status() for key, proc in self.processes.items()}
        return json.dumps(status_report)

    def stopProcessId(self, id):
        if id in self.processes:
            self.processes[id].stopProcess()
            return json.dumps({"status": "success", "message": f"Stopped {id}"})
        return json.dumps({"status": "error", "message": f"Process {id} not found"})

    def startProcessId(self, id):
        if id in self.processes:
            self.processes[id].launchProcess()
            return json.dumps({"status": "success", "message": f"Started {id}"})
        return json.dumps({"status": "error", "message": f"Process {id} not found"})

    def restartProcessId(self, id):
        if id in self.processes:
            self.processes[id].restartProcess()
            return json.dumps({"status": "success", "message": f"Restarted {id}"})
        return json.dumps({"status": "error", "message": f"Process {id} not found"})

    def endProgram(self):
        # Stop all managed processes before exiting
        for proc in self.processes.values():
            proc.stopProcess()
        sys.exit(0)

    def processConsole(self, line):
        """
        Processes a single-line command.
        Expected formats:
         - "status"
         - "reload"
         - "exit"
         - "stop <process_id>"
         - "start <process_id>"
         - "restart <process_id>"
        """
        # Split the command line into tokens, and convert command to lowercase
        tokens = line.strip().split()
        if not tokens:
            return json.dumps({"status": "error", "message": "Empty command"})

        cmd = tokens[0].lower()
        arg = " ".join(tokens[1:]) if len(tokens) > 1 else None

        if cmd == "status":
            return self.checkStatus()
        elif cmd == "stop":
            if arg:
                return self.stopProcessId(arg)
            return json.dumps({"status": "error", "message": "Missing process ID for stop"})
        elif cmd == "start":
            if arg:
                return self.startProcessId(arg)
            return json.dumps({"status": "error", "message": "Missing process ID for start"})
        elif cmd == "restart":
            if arg:
                return self.restartProcessId(arg)
            return json.dumps({"status": "error", "message": "Missing process ID for restart"})
        elif cmd == "reload":
            self.updateParsing()
            return json.dumps({"status": "success", "message": "Configuration reloaded"})
        elif cmd == "exit":
            self.endProgram()
        else:
            return json.dumps({"status": "error", "message": "Unknown command"})

def setup_server(port):
    """Initialize and return a configured server socket."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    server.listen()
    print(f"Listening on {HOST}:{port}...")
    return server

def handle_client(conn, addr, taskmaster):
    """Handle incoming client connection."""
    print(f"Connected by {addr}")
    try:
        data = conn.recv(1024)
        if data:
            response = process_command(data, taskmaster)
            conn.sendall(response)
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()

def process_command(data, taskmaster):
    """
    Process the received data (a single-line command as JSON string).
    The JSON is expected to contain a single key "command" with a string value.
    """
    try:
        cmd_data = json.loads(data.decode())
        line = cmd_data.get("command", "")
        print(f"Received command line: {line}")
        response = taskmaster.processConsole(line)
    except json.JSONDecodeError:
        response = json.dumps({"status": "error", "message": "Malformed JSON"})
    return response.encode()

def start_daemon(port, taskmaster):
    """Start the daemon server and handle incoming connections."""
    server = setup_server(port)
    try:
        while True:
            conn, addr = server.accept()
            handle_client(conn, addr, taskmaster)
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
    
    # Create a TaskMaster instance which starts up the managed processes
    taskmaster = TaskMaster()
    # Start the daemon to listen for JSON commands
    start_daemon(port, taskmaster)

