#!/bin/python
import socket
import sys
import json
from ManagedProcess import ManagedProcess
from configParsing import add_nprocs
from Daemonclass import Daemon, start_daemon
from Taskmaster import TaskMaster

if __name__ == "__main__":
    """if len(sys.argv) != 2:
        print("Usage: python script.py <port>")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port. Please enter a valid integer.")
        sys.exit(1)"""

    port = 7777
    
    # Create a TaskMaster instance which starts up the managed processes
    taskmaster = TaskMaster()
    daemon = Daemon(taskmaster)
    # Start the daemon to listen for JSON commands
    start_daemon(port, daemon)

