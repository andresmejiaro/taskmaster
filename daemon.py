#!/bin/python
import os
import asyncio
import socket
import sys
import json
import signal
from ManagedProcess import ManagedProcess
from configParsing import add_nprocs
from Daemonclass import Daemon, start_daemon
from Taskmaster import TaskMaster

ROUTER_HOST = '127.0.0.1'
g_port = 7777

def send_command(command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((ROUTER_HOST, g_port))
            message = json.dumps({"command": command})
            client.sendall(message.encode())
    except ConnectionRefusedError:
        print("Daemon is down. Unable to connect.")
    except Exception as e:
        print("An error occurred:", e)

def daemonize():
    if os.fork() > 0:
        sys.exit(0)
    os.setsid()
    if os.fork() > 0:
        sys.exit(0)
    sys.stdout.flush()
    sys.stderr.flush()
    with open('/dev/null', 'r') as dev_null:
        os.dup2(dev_null.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a') as dev_null:
        os.dup2(dev_null.fileno(), sys.stdout.fileno())
        os.dup2(dev_null.fileno(), sys.stderr.fileno())


loop = asyncio.get_event_loop()

loop.add_signal_handler(signal.SIGTERM, lambda: send_command("poweroffs"))
loop.add_signal_handler(signal.SIGHUP, lambda: send_command("reloads"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <port>")
        sys.exit(1)
    try:
        port = int(sys.argv[1])
        g_port = port
    except ValueError:
        print("Invalid port. Please enter a valid integer.")
        sys.exit(1)
    daemonize()
    taskmaster = TaskMaster()
    daemon = Daemon(taskmaster)
try:
    loop.run_until_complete(start_daemon(port, daemon))
except KeyboardInterrupt:
    print("\nReceived KeyboardInterrupt. Exiting...")
except RuntimeError as e:
    if str(e) == "Event loop stopped before Future completed.":
        print("Shutdown complete (runtime error caught).")
    else:
        raise
finally:
    tasks = asyncio.all_tasks(loop)
    for task in tasks:
        task.cancel()
    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    loop.close()
    print("Event loop closed cleanly.")
