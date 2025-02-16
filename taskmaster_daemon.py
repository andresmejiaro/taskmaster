from ManagedProcess import ManagedProcess
import json
import socket
import os

SOCKET_PATH = "/tmp/daemon_socket"

class TaskMaster:
    def __init__(self):
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.processes = {}
        
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
        self.server.bind(SOCKET_PATH)
        self.server.listen(5)
        
        self.updateParsing()
        for proc in self.processes.values():
            proc.launchProcess()

    def parseJson(self, route):
        with open(route, "r") as file:
            return json.load(file)

    def updateParsing(self):
        outJson = self.parseJson("conf.json")
        self.processes = {key: ManagedProcess(value) for key, value in outJson.items()}

    def updateProcesses(self):
        for value in self.processes.values():
            value.launchProcess()

    def checkStatus(self):
        for key, proc in self.processes.items():
            print(f"{key}: {proc.status()}")

    def stopProcessId(self, id):
        if id in self.processes:
            self.processes[id].stopProcess()

    def startProcessId(self, id):
        if id in self.processes:
            self.processes[id].launchProcess()

    def restartProcessId(self, id):
        if id in self.processes:
            self.processes[id].restartProcess()

    def endProgram(self):
        self.server.close()
        os.remove(SOCKET_PATH)
        exit(0)

    def processConsole(self, command):
        commands = command.split()
        if not commands:
            return
        
        match commands[0]:
            case "checkStatus":
                self.checkStatus()
            case "stop":
                if len(commands) > 1:
                    self.stopProcessId(commands[1])
            case "start":
                if len(commands) > 1:
                    self.startProcessId(commands[1])
            case "restart":
                if len(commands) > 1:
                    self.restartProcessId(commands[1])
            case "reloadConfig":
                self.updateParsing()
            case "exit":
                self.endProgram()

    def Loop(self):
        while True:
            conn, _ = self.server.accept()
            data = conn.recv(1024)
            if data:
                try:
                    command = json.loads(data.decode())
                    if isinstance(command, str):
                        self.processConsole(command)
                    else:
                        print("Invalid command format")
                except json.JSONDecodeError:
                    print("Received invalid JSON")
                conn.sendall(b"ACK")


def main():
    taskmaster = TaskMaster()
    taskmaster.Loop()

if __name__ == "__main__":
    main()
