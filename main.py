from taskmaster_daemon import start_taskmaster
from shell import start_shell
import subprocess
import time


def main():
    subprocess.Popen(["python", "taskmaster_daemon.py"])
    time.sleep(2)
    start_shell()

if __name__== "__main__":
    main()
