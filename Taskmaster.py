import json
from configParsing import add_nprocs, updateParsing
from ManagedProcess import ManagedProcess

class TaskMaster:
    def __init__(self):
        self.processes, self.oldJson = updateParsing("conf.json")
        self.nameProcess()
        for proc in self.processes.values():
            if proc.autostart:
                proc.launchProcess()
    
    def nameProcess(self):
        for key,value in self.processes.items():
            value.name = key

    def updateParsing(self):
        _, newParsing = updateParsing("conf.json")
        common = {key: value for key, value in newParsing.items() if key in self.oldJson.keys() and self.oldJson[key] ==  value}
        notCommon = {key: value for key, value in newParsing.items() if key not in common.keys()} 
        common = add_nprocs(common)
        notCommon = add_nprocs(notCommon)
        for key in self.processes.keys():
            if key not in common:
                self.processes[key].drop = True
                self.stopProcessId(key)
        for key, value in notCommon.items():
            self.processes[key] = ManagedProcess(value)
            self.processes[key].name = key
            if self.processes[key].autostart:
                self.processes[key].launchProcess()
        
        self.oldJson = newParsing


    def updateProcesses(self):
        to_del = []
        for key, proc in self.processes.items():
            drop = proc.updateStatus()
            if drop:
                to_del.append(key)    
        for key in to_del:
            del self.processes[key]

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

 