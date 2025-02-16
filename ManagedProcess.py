import subprocess, shlex, signal
from enum import Enum
from datetime import datetime



class ProcessStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    STARTiNG = "starting"
    CRASHED = "crashed"
    STOPING = "stoping"


class ReestartOptions(Enum):
    ALWAYS = "always"
    NEVER = "never"
    CRASH = "crash"

class ManagedProcess:
    def __init__(self, jsonAtt):
        self.command = jsonAtt["cmd"]
        self.numprocs = jsonAtt.get("numprocs",1)
        self.umask = jsonAtt.get("umask",22)
        self.workingdir = jsonAtt.get("workingdir",".")
        self.autostart = jsonAtt.get("autostart",False)
        self.exitcodes = jsonAtt.get("exitcodes",[0])
        self.starttime = jsonAtt.get("starttime",0)
        signal_name = jsonAtt.get("stopsignal","TERM")  # Or any other signal name without the 'SIG' prefix.
        try:
            sig = getattr(signal, "SIG" + signal_name)
        except AttributeError:
            print(f"Invalid signal name: SIG{signal_name}, using SIGTERM instead to finish")
            sig = getattr(signal, "SIGTERM")
        self.stopsignal = sig
        self.stoptime = jsonAtt.get("stoptime",10)
        self.stdout = jsonAtt.get("stdout","/dev/null")
        self.stderr = jsonAtt.get("stderr","/dev/null")
        self.env = jsonAtt.get("env",{})
        self.status = ProcessStatus.STOPPED
        self.initTime = None
        self.breakTime = None
        self.process = None
        self.restarting = 0
       

    def updateStatus(self):
        
        if self.process is None:
            return
        pollresult = self.process.poll()
        if self.restarting == True and \
            self.status == ProcessStatus.RUNNING:
            self.restarting = False
        if self.restarting == True:
            self.restartProcess()
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
            case ProcessStatus.STOPING:
                self.stopProcess()


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
 
        

    def stopProcess(self):

        if self.breakTime is not None:
            difftime = datetime.now() - self.breakTime()
        else:
            difftime = None
        if self.status == ProcessStatus.STOPING and difftime is not None :
            if difftime > self.stoptime:
                self.process.kill()
                self.status = ProcessStatus.STOPPED           
        if self.status == ProcessStatus.RUNNING:
            self.status = ProcessStatus.STOPING
            self.process.send_signal(self.stopsignal)
            self.breakTime = datetime.now()


    def restartProcess(self):
        self.restarting = True
        if self.status == ProcessStatus.RUNNING:
            self.stopProcess()
        if self.status in (ProcessStatus.STOPPED, ProcessStatus.CRASHED)
            self.launchProcess()

    def outputGet(self):
        pass

    