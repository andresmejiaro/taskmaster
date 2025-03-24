import json
from configParsing import add_nprocs
from ManagedProcess import ManagedProcess

class TaskMaster:
    def __init__(self):
        self.updateParsing()
        # Launch all processes at initialization
        for proc in self.processes.values():
            if proc.autostart:
                proc.launchProcess()

    def parseJson(self, route):
        with open(route, "r") as file:
            return json.load(file)

    def updateParsing(self):
        outJson = self.parseJson("conf.json")
        outJson = add_nprocs(outJson)
        self.processes = {key: ManagedProcess(value) for key, value in outJson.items()}

    def updateProcesses(self):
        for proc in self.processes.values():
            proc.updateStatus()

    def checkStatus(self):
        self.updateProcesses()
        status_report = {key: proc.status.value for key, proc in self.processes.items()}
        string = str(json.dumps(status_report))
        return json.dumps({"status": "success", "message": f"{string}"})

    def stopProcessId(self, id):
        if id in self.processes:
            self.processes[id].stopProcess()
            return json.dumps({"status": "success", "message": f"Stopped {id}"})
        return json.dumps({"status": "error", "message": f"Process {id} not found"})

    def startProcessId(self, id):
        if id in self.processes:
            self.processes[id].launchProcess(manual = True)
            return json.dumps({"status": "success", "message": f"Started {id}"})
        return json.dumps({"status": "error", "message": f"Process {id} not found"})

    def restartProcessId(self, id):
        if id in self.processes:
            self.processes[id].restartProcess()
            return json.dumps({"status": "success", "message": f"Restarted {id}"})
        return json.dumps({"status": "error", "message": f"Process {id} not found"})

 