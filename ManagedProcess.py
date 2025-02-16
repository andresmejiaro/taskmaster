import subprocess, shlex
from enum import Enum
from datetime import datetime



class ProcessStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    STARTiNG = "starting"
    CRASHED = "crashed"





class ManagedProcess:
    def __init__(self, jsonAtt):
        self.command = jsonAtt["cmd"]
        self.numprocs = jsonAtt.get("numprocs",1)
        self.umask = jsonAtt.get("umask",22)
        self.workingdir = jsonAtt.get("workingdir",".")
        self.autostart = jsonAtt.get("autostart",False)
        self.exitcodes = jsonAtt.get("exitcodes",[0])
        self.starttime = jsonAtt.get("starttime",0)
        self.stopsignal = jsonAtt.get("stopsignal","TERM")
        self.stoptime = jsonAtt.get("stoptime",10)
        self.stdout = jsonAtt.get("stdout","/dev/null")
        self.stderr = jsonAtt.get("stderr","/dev/null")
        self.env = jsonAtt.get("env",{})
        self.status = ProcessStatus.STOPPED
        self.initTime = None
        self.process = None
       

    def updateStatus(self):
        
        if self.process is None:
            return
        pollresult = self.process.poll()
        match self.status:
            case ProcessStatus.STOPPED:
                pass
            case ProcessStatus.STARTiNG:
                if pollresult is None and \
                    (datetime.now() - self.initTime).total_seconds() > \
                    self.starttime:
                    self.status = ProcessStatus.RUNNING
                elif pollresult in self.exitcodes:
                    self.status = ProcessStatus.STOPPED
                elif pollresult not in self.exitcodes:
                    self.status = ProcessStatus.CRASHED


    def launchProcess(self):
        #sp.Popen(self.command)
        command = shlex.split(self.command)

        
        try:
            with open(self.stdout,"w") as outfile, open(self.stderr,"w") as errfile:
                    try:
                        self.process = subprocess.Popen(command,
                        stdout=outfile, stderr=errfile)
                        self.status = ProcessStatus.STARTiNG
                        self.initTime = datetime.now()
                    except OSError as e:
                        self.status = ProcessStatus.CRASHED
                        print(f'Error launching the command: {e}')
        except (IOError, OSError) as e:
            self.status = ProcessStatus.CRASHED
            print(f"Error opening the files: {e}")
 
        

    def killProcess(self):
        pass

    def restartProcess(self):
        self.killProcess()
        self.launchProcess()

    def outputGet(self):
        pass

    