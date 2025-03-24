#!/bin/python
import asyncio
import json
import sys
from ManagedProcess import ManagedProcess
from configParsing import add_nprocs

HOST = '127.0.0.1'

class Daemon:
    def __init__(self, taskMaster):
        self.taskMaster = taskMaster
    
    async def processConsole(self, line):
        tokens = line.strip().split()
        if not tokens:
            return json.dumps({"status": "error", "message": "Empty command"})

        cmd = tokens[0].lower()
        arg = " ".join(tokens[1:]) if len(tokens) > 1 else None

        if cmd == "status":
            return self.taskMaster.checkStatus()
        elif cmd == "stop":
            if arg:
                return self.taskMaster.stopProcessId(arg)
            return json.dumps({"status": "error", "message": "Missing process ID for stop"})
        elif cmd == "start":
            if arg:
                return self.taskMaster.startProcessId(arg)
            return json.dumps({"status": "error", "message": "Missing process ID for start"})
        elif cmd == "restart":
            if arg:
                return self.taskMaster.restartProcessId(arg)
            return json.dumps({"status": "error", "message": "Missing process ID for restart"})
        elif cmd == "reload":
            self.taskMaster.updateParsing()
            return json.dumps({"status": "success", "message": "Configuration reloaded"})
        elif cmd == "exit":
            await self.endProgram()
        else:
            return json.dumps({"status": "error", "message": "Unknown command"})
    
    async def endProgram(self):
        for proc in self.taskMaster.processes.values():
            proc.stopProcess()
        sys.exit(0)

async def handle_client(reader, writer, daemon):
    addr = writer.get_extra_info('peername')
    print(f"Connected by {addr}")
    try:
        data = await reader.read(1024)
        if data:
            response = await process_command(data, daemon)
            writer.write(response)
            await writer.drain()
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def process_command(data, daemon):
    try:
        cmd_data = json.loads(data.decode())
        line = cmd_data.get("command", "")
        print(f"Received command line: {line}")
        response = await daemon.processConsole(line)
    except json.JSONDecodeError:
        response = json.dumps({"status": "error", "message": "Malformed JSON"})
    return response.encode()

async def per_frame_function(daemon):
    while True:
        daemon.taskMaster.checkStatus()
        await asyncio.sleep(0.1)  # Adjust the sleep for your timing needs

async def start_daemon(port, daemon):
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, daemon), HOST, port)
    print(f"Listening on {HOST}:{port}...")

    async with server:
        # Run both the server and the per-frame function concurrently
        await asyncio.gather(
            server.serve_forever(),
            per_frame_function(daemon)
        )