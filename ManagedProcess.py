import subprocess, shlex, signal, json
from enum import Enum
from datetime import datetime
from logs import logger
import os


class ProcessStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    STARTING = "starting"
    CRASHED = "crashed"
    STOPING = "stoping"


class ReestartOptions(Enum):
    ALWAYS = "always"
    NEVER = "never"
    CRASH = "crash"

class ManagedProcess:
    def __init__(self, jsonAtt):
        self.command = jsonAtt["cmd"]
        self.name = self.command
        self.numprocs = jsonAtt.get("numprocs",1)
        umask_raw = jsonAtt.get("umask", "022")
        self.umask = int(umask_raw, 8) if isinstance(umask_raw, str) else umask_raw
        self.workingdir = jsonAtt.get("workingdir",".")
        self.autostart = jsonAtt.get("autostart",False)
        self.exitcodes = jsonAtt.get("exitcodes",[0])
        self.starttime = jsonAtt.get("starttime",0)
        self.startretries = jsonAtt.get("startretries",0)
        signal_name = jsonAtt.get("stopsignal","TERM")  
        try:
            sig = getattr(signal, "SIG" + signal_name)
        except AttributeError:
            logger.error(f"{self.command} Invalid signal name: SIG{signal_name}, using SIGTERM instead to finish")
            sig = getattr(signal, "SIGTERM")
        self.stopsignal = sig
        self.stoptime = jsonAtt.get("stoptime",10)
        self.stdout = jsonAtt.get("stdout","/dev/null")
        self.stderr = jsonAtt.get("stderr","/dev/null")
        self.env = os.environ.copy()
        tmp_env = jsonAtt.get("env",{})
        self.env.update(tmp_env)
        self.status = ProcessStatus.STOPPED
       
        self.initTime = None
        self.breakTime = None
        self.process = None
        self.restarting = 0
        self.restartCounter = 0
        self.restartOption = jsonAtt.get("autorestart","never")
        self.drop = False
        match self.restartOption:
            case "always":
                self.restartOption = ReestartOptions.ALWAYS
            case "unexpected":
                self.restartOption = ReestartOptions.CRASH
            case "never":
                self.restartOption = ReestartOptions.NEVER
            case _:
                self.restartOption = ReestartOptions.NEVER
                logger.error(f"{self.command} Invalid restart option defaulting to never")

    def updateStatus(self):
        if self.process is None:
            return self.drop
        pollresult = self.process.poll()
        if self.restarting == True and \
            self.status == ProcessStatus.RUNNING:
            self.restarting = False
        if self.restarting == True:
            self.restartProcess()
        match self.status:
            case ProcessStatus.STOPPED:
                if self.drop == True:
                    return True
                elif self.restartOption == ReestartOptions.ALWAYS:
                    self.restartProcess()
            case ProcessStatus.STARTING:
                if pollresult is None:
                    if (datetime.now() - self.initTime).total_seconds() > \
                    self.starttime:
                        self.status = ProcessStatus.RUNNING
                        logger.debug(f"{self.name} changed status to RUNNING")
                else:
                    if pollresult in self.exitcodes:
                        self.status = ProcessStatus.STOPPED
                        logger.debug(f"{self.name} changed status to STOPPED")
                    else:
                        self.status = ProcessStatus.CRASHED
                        logger.debug(f"{self.name} changed status to CRASHED")
            case ProcessStatus.STOPING:
                self.stopProcess(pollresult)
            case ProcessStatus.RUNNING:
                if pollresult is not None and pollresult in self.exitcodes:
                    self.status = ProcessStatus.STOPPED
                    logger.debug(f"{self.name} changed status to STOPPED")
                elif pollresult is not None and pollresult not in self.exitcodes:
                    self.status = ProcessStatus.CRASHED
                    logger.debug(f"{self.name} changed status to CRASHED")
            case ProcessStatus.CRASHED:
                if self.drop == True:
                    return True
                if self.restartOption in [ReestartOptions.ALWAYS, ReestartOptions.CRASH]:
                    self.restartProcess()
        return False


    def launchProcess(self, manual = False):
        #sp.Popen(self.command)
        if manual:
            self.restartCounter = 0
        command = shlex.split(self.command)
        try:
            with open(self.stdout,"w") as outfile, open(self.stderr,"w") as errfile:
                    try:
                        self.process = subprocess.Popen(command,
                        stdout=outfile, stderr=errfile, cwd = self.workingdir, umask = self.umask,
                        env = self.env)
                        self.status = ProcessStatus.STARTING
                        logger.debug(f"{self.name} changed status to STARTING")
                        self.initTime = datetime.now()
                    except OSError as e:
                        self.status = ProcessStatus.CRASHED
                        logger.debug(f"{self.name} changed status to CRASHED")
                        logger.error(f"{self.name} Error launching the command {e}")
                        print(f'Error launching the command: {e}')
        except (IOError, OSError) as e:
            self.status = ProcessStatus.CRASHED
            logger.debug(f"{self.name} changed status to CRASHED")
            logger.error(f"{self.name} Error opening stdout or stderr {e}")
            print(f"Error opening the files: {e}")
 
        

    def stopProcess(self, pollresult = None):
        if self.breakTime is not None:
            difftime = datetime.now() - self.breakTime
        else:
            difftime = None
        if self.status == ProcessStatus.STOPING and difftime is not None :
            if pollresult is not None:
               self.status = ProcessStatus.STOPPED
               logger.debug(f"{self.name} changed status to STOPPED")
            elif difftime.seconds > self.stoptime:
                self.process.kill()
                self.status = ProcessStatus.STOPPED           
        if self.status in [ProcessStatus.RUNNING, ProcessStatus.STARTING]:
            self.status = ProcessStatus.STOPING
            logger.debug(f"{self.name} changed status to STOPPING")
            self.process.send_signal(self.stopsignal)
            self.breakTime = datetime.now()


    def restartProcess(self):
        if self.restartCounter >= self.startretries:
            return 
        self.restarting = True
        if self.status == ProcessStatus.RUNNING:
            self.stopProcess()
        if self.status in (ProcessStatus.STOPPED, ProcessStatus.CRASHED):
            self.restartCounter += 1
            self.launchProcess()

    def statusjson(self):
        status = json.dumps({"status": self.status.value, "restarting" : self.restarting})
        return status
    