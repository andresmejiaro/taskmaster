from ManagedProcess import ManagedProcess
import json
import sys


def parseJson(route):
    with open(route, "r") as file:
        result = json.load(file)
    return result

def updateParsing(processes):
    try:
        outJson = parseJson("conf.json")
    except BaseException as e:
        print("error parsing the config file")
        sys.exit()
    for key, value in outJson.items():
        processes[key] = ManagedProcess(value)
