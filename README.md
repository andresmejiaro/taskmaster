# Taskmaster

Taskmaster is a lightweight process supervisor written in Python. It reads a JSON configuration and manages one or more child processes, providing a simple interface to monitor and control them.

## Features

- Launch and monitor multiple processes with custom environment, working directory, and I/O redirection.
- Auto-start processes on daemon startup and support for different autorestart policies.
- Hot configuration reload to add or drop processes without restarting the daemon.
- Interactive client for issuing commands such as `status`, `start`, `stop`, `restart`, `reload`, and `poweroff`.

## Getting Started

### Requirements

- Python 3.10 or newer (uses `asyncio` and `enum`).

### Configuration

Processes are defined in `conf.json`. Each entry specifies the command to run and optional behaviour such as automatic restarts, log files, and environment variables. An example configuration is included in the repository and looks like:

```json
{
    "ls": {
        "cmd": "/bin/ls",
        "autostart": true,
        "numprocs": 2,
        "stdout": "/tmp/ls"
    }
}
```

See [conf.json](conf.json) for a complete example with more options.

### Running the daemon

```bash
python daemon.py <port>
```

The daemon loads `conf.json`, names each process, and launches those marked for auto-start on boot.

### Using the client

```bash
python client.py <port>
```

Once connected, you can issue commands from the interactive prompt:

- `status` – show the state of each managed process.
- `start <name>` / `stop <name>` / `restart <name>` – control a specific process.
- `reload` – re-read `conf.json` and apply configuration changes.
- `poweroff` – stop all processes and shut down the daemon.

## Logging

Runtime information is written to `taskmaster.log` and the system log using Python's `logging` module.

## License

This project is provided as-is without warranty. Use it as a learning reference or adapt it to your needs.

