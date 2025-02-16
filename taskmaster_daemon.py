from ManagedProcess import ManagedProcess
import json
import time
import socket
import os

SOCKET_PATH = "/tmp/daemon_socket"

class taskmaster():

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    processes = {}

    def __init__(self):
        super().__init__()

        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)
        self.server.bind(SOCKET_PATH)
        self.server.listen(5)

        self.updateParsing(self.processes)
        for _, proc in self.processes.items():
            proc.launchProcess()


    def parseJson(self, route):
        with open(route, "r") as file:
            result = json.load(file)
        return result

    def updateParsing(self):
        outJson = self.parseJson("conf.json")
        for key, value in outJson.items():
            self.processes[key] = ManagedProcess(value)


    def updateProcesses(self, processes):
        for _, value in processes:
            value.launchPrcess()

    def checkStatus(self):
        pass

    def stopProcessId(self, id):
        pass

    def endProgram(self):
        self.conn.close()
        pass

    def processConsole(self):
        consoleCommand = "command"
        match consoleCommand:
            case "checkStatus":
                self.checkStatus()
            case "stop id":
                self.stopProcessId("id")
            case "start id":
                self.startProcessId("id")
            case "restart id":
                self.restartProcessId("id")
            case "reloadConfig":
                self.updateParsing()
            case "exit":
                self.endProgram()

    def Loop(self):
        while True:
            conn, _ = self.server.accept()
            data = conn.recv(1024)
            if data:
                ''' chatgpt here i need to convert the data recived from json to something so i can execute the function above '''
                print(f"Received: {data.decode()}")
                conn.sendall(b"ACK")


def start_taskmaster(taskmaster):
    taskmaster.Loop()

def main():
    ''' idk here chatgpt is this ok?'''
    hello = taskmaster
    start_taskmaster(hello)

if __name__== "__main__":
    main()
