from configParsing import parseJson, updateParsing
import time



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


def main():
    processes = {}
    updateParsing(processes)
    for _,proc in processes.items():
        proc.launchProcess()
    while True:
        time.sleep(2)
        for name , proc in processes.items():
            proc.updateStatus()
            print(f"Name:{name}, status {proc.status}")


if __name__== "__main__":
    main()