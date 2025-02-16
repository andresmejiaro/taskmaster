from ManagedProcess import ManagedProcess
import json

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
