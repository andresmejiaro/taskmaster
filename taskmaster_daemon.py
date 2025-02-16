from ManagedProcess import ManagedProcess
import json
import time
import socket
import os

SOCKET_PATH = "/tmp/daemon_socket"

class taskmaster():
    def parseJson(route):
        with open(route, "r") as file:
            result = json.load(file)
        return result

    def updateParsing(processes):
        outJson = parseJson("conf.json")
        for key, value in outJson.items():
            processes[key] = ManagedProcess(value)


    def updateProcesses(processes):
        for _, value in processes:
            value.launchPrcess()

    def checkStatus():
        pass

    def stopProcessId(id):
        pass

    def endProgram():
        pass

    def processConsole():
        consoleCommand = "command"
        match consoleCommand:
            case "checkStatus":
                checkStatus()
            case "stop id":
                stopProcessId("id")
            case "start id":
                startProcessId("id")
            case "restart id":
                restartProcessId("id")
            case "reloadConfig":
                updateParsing()
            case "exit":
                endProgram()

def start_taskmaster():

    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)

    processes = {}
    updateParsing(processes)
    for _,proc in processes.items():
        proc.launchProcess()
    while True:
        conn, _ = server.accept()
        data = conn.recv(1024)
        if data:
            print(f"Received: {data.decode()}")
            conn.sendall(b"ACK")
        conn.close()

        '''
        for name , proc in processes.items():
            proc.updateStatus()
            print(f"Name:{name}, status {proc.status}")
        '''

def main():
    start_taskmaster()

if __name__== "__main__":
    main()
