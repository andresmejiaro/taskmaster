import subprocess


class ManagedProcess:
    def __init__(self, jsonAtt):
        self.command = jsonAtt["cmd"]


    def launchProcess(self):
        #sp.Popen(self.command)

        process = subprocess.Popen([self.command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()

# Print results
        print(stdout.decode())  # Decode bytes to string
        print(stderr.decode())  # Print errors if any

        
        
    

    def checkStatus(self):
        pass

    def killProcess(self):
        pass

    def restartProcess(self):
        self.killProcess()
        self.launchProcess()

    def outputGet(self):
        pass

    