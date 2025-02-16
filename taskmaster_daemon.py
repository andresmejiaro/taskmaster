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
            if proc.autostart == True:
                proc.launchProcess()

    #Read the original JSON FILE
    def parseJson(self, route):
        with open(route, "r") as file:
            return json.load(file)

    #Crate the processes based on the Json file 
    ## Needs updating for "hot updating"
    def updateParsing(self):
        outJson = self.parseJson("conf.json")
        self.processes = {key: ManagedProcess(value) for key, value in outJson.items()}

#    def updateProcesses(self):
#        for value in self.processes.values():
#            value.launchProcess()

    def checkStatus(self):
        status_report = {key: proc.statusjson() for key, proc in self.processes.items()}
        w = json.dumps(status_report)
        print(w)
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

    def Loop(self):
        while True:
            conn, _ = self.server.accept()
            data = conn.recv(1024)
            if data:
                try:
                    command = json.loads(data.decode())
                    response = self.processConsole(command)
                except json.JSONDecodeError:
                    response = json.dumps({"status": "error", "message": "Invalid JSON"})
                
                conn.sendall(response.encode())

            for _, proc in self.processes.items():
                proc.updateStatus()
            conn.close()
            


def main():
    taskmaster = TaskMaster()
    taskmaster.Loop()

if __name__ == "__main__":
    main()
