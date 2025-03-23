#!/bin/python
from ManagedProcess import ManagedProcess
import json
import socket
import os

SOCKET_PATH = "/tmp/daemon_socket"

class TaskMaster:
    def __init__(self):
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
        self.server.close()
        os.remove(SOCKET_PATH)
        exit(0)

    def processConsole(self, command):
        cmd = command.get("command")
        arg = command.get("argument")

        if cmd == "STATUS":
            return self.checkStatus()
        elif cmd == "STOP":
            return self.stopProcessId(arg)
        elif cmd == "START":
            return self.startProcessId(arg)
        elif cmd == "RESTART":
            return self.restartProcessId(arg)
        elif cmd == "RELOAD":
            self.updateParsing()
            return json.dumps({"status": "success", "message": "Configuration reloaded"})
        elif cmd == "EXIT":
            self.endProgram()
        return json.dumps({"status": "error", "message": "Unknown command"})
