from ManagedProcess import ManagedProcess
import json
import sys
import copy 


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
    processes[key] = ManagedProcess(value)

def add_nprocs(outJson):
    result = {}
    for key, val in outJson.items():
        if isinstance(val, dict) and "numprocs" in val and val["numprocs"] != 1:
            for i in range(val["numprocs"]):
                result[f"{key}{i}"] = copy.deepcopy(val)
                if "stdout" in result[f"{key}{i}"].keys():
                    result[f"{key}{i}"]["stdout"] = result[f"{key}{i}"]["stdout"] + f"_{i}"
                if "stderr" in result[f"{key}{i}"].keys():
                    result[f"{key}{i}"]["stderr"] = result[f"{key}{i}"]["stderr"] + f"_{i}"  
        else:
            result[key] = val
    return result