import cmd
import signal
import logging
import socket
import sys

SOCKET_PATH = "/tmp/daemon_socket"

# Configure logging
logging.basicConfig(
    filename='taskmaster.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ProgramShell(cmd.Cmd):
    """Shell to interact with the daemon"""
    prompt = "\033[92mtaskmaster> \033[0m"  # Green prompt

    def __init__(self):
        super().__init__()
        try:
            self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.client.connect(SOCKET_PATH)
        except Exception as e:
            print(f"\033[91m[ERROR] Failed to connect to daemon: {e}\033[0m")
            sys.exit(1)

    def exec_and_print(self, message):
        try:
            self.client.sendall(message.encode())
            response = self.client.recv(4096).decode()
            print(f"\033[94m{response}\033[0m")  # Blue response
        except Exception as e:
            print(f"\033[91m[ERROR] Communication error: {e}\033[0m")

    def log_and_print(self, level, message):
        print(message)
        if level == "info":
            logging.info(message)
        elif level == "error":
            logging.error(message)

    def do_status(self, arg):
        "Show the status of all programs"
        self.log_and_print("info", "[INFO] Fetching status of all programs...")
        self.exec_and_print("STATUS")

    def do_start(self, arg):
        "Start a specific program: start <program_name>"
        if not arg:
            self.log_and_print("error", "[ERROR] Please specify a program to start.")
        else:
            self.log_and_print("info", f"[INFO] Starting program: {arg}")
            self.exec_and_print(f"START {arg}")

    def do_stop(self, arg):
        "Stop a specific program: stop <program_name>"
        if not arg:
            self.log_and_print("error", "[ERROR] Please specify a program to stop.")
        else:
            self.log_and_print("info", f"[INFO] Stopping program: {arg}")
            self.exec_and_print(f"STOP {arg}")

    def do_restart(self, arg):
        "Restart a specific program: restart <program_name>"
        if not arg:
            self.log_and_print("error", "[ERROR] Please specify a program to restart.")
        else:
            self.log_and_print("info", f"[INFO] Restarting program: {arg}")
            self.exec_and_print(f"RESTART {arg}")

    def do_reload(self, arg):
        "Reload the configuration file"
        self.log_and_print("info", "[INFO] Reloading configuration file...")
        self.exec_and_print("RELOAD")

    def do_exit(self, arg):
        "Exit the shell"
        self.exec_and_print("EXIT")
        self.log_and_print("info", "[INFO] Exiting shell...")
        self.client.close()
        return True
    
    def do_EOF(self, arg):
        "Handle Ctrl+D (EOF) to exit the shell"
        self.log_and_print("info", "\n[INFO] Exiting shell...")
        self.client.close()
        return True

    def default(self, line):
        "Handle unknown commands"
        self.log_and_print("error", f"[ERROR] Unknown command: {line}. Type 'help' to see the command list.")

    def signal_handler(self, signum, frame):
        self.log_and_print("info", "\n[INFO] Exiting shell...")
        self.client.close()
        sys.exit(0)

if __name__ == "__main__":
    shell = ProgramShell()
    signal.signal(signal.SIGINT, shell.signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, shell.signal_handler)  # Handle termination signals
    shell.cmdloop()
