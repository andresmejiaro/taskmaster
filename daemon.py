#!/bin/python
import os
import asyncio
import socket
import sys
import json
from ManagedProcess import ManagedProcess
from configParsing import add_nprocs
from Daemonclass import Daemon, start_daemon
from Taskmaster import TaskMaster


def daemonize():
    # Fork the first time
    if os.fork() > 0:
        sys.exit(0)  # Exit parent

    # Create a new session
    os.setsid()

    # Fork again to prevent reacquiring a terminal
    if os.fork() > 0:
        sys.exit(0)

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    with open('/dev/null', 'r') as dev_null:
        os.dup2(dev_null.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a') as dev_null:
        os.dup2(dev_null.fileno(), sys.stdout.fileno())
        os.dup2(dev_null.fileno(), sys.stderr.fileno())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <port>")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port. Please enter a valid integer.")
        sys.exit(1)
    daemonize()
    # Create a TaskMaster instance which starts up the managed processes
    taskmaster = TaskMaster()
    daemon = Daemon(taskmaster)
    asyncio.run(start_daemon(port, daemon))
