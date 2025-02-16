import cmd
import signal
import logging

# Configure logging
logging.basicConfig(
    filename='shell.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ProgramShell(cmd.Cmd):
    prompt = "taskmaster> "

    def log_and_print(self, level, message):
        print(message)
        if level == "info":
            logging.info(message)
        elif level == "error":
            logging.error(message)

    def do_status(self, arg):
        "Show the status of all programs"
        self.log_and_print("info", "[INFO] Fetching status of all programs...")

    def do_start(self, arg):
        "Start a specific program: start <program_name>"
        if not arg:
            self.log_and_print("error", "[ERROR] Please specify a program to start.")
        else:
            self.log_and_print("info", f"[INFO] Would run: start {arg}")

    def do_stop(self, arg):
        "Stop a specific program: stop <program_name>"
        if not arg:
            self.log_and_print("error", "[ERROR] Please specify a program to stop.")
        else:
            self.log_and_print("info", f"[INFO] Would run: stop {arg}")

    def do_restart(self, arg):
        "Restart a specific program: restart <program_name>"
        if not arg:
            self.log_and_print("error", "[ERROR] Please specify a program to restart.")
        else:
            self.log_and_print("info", f"[INFO] Would run: restart {arg}")

    def do_reload(self, arg):
        "Reload the configuration file"
        self.log_and_print("info", "[INFO] Reloading configuration file...")

    def do_exit(self, arg):
        "Exit the shell"
        self.log_and_print("info", "[INFO] Exiting shell...")
        return True
    
    def do_EOF(self, arg):
        "Handle Ctrl+D (EOF) to exit the shell"
        self.log_and_print("info", "\n[INFO] Exiting shell...")
        return True

    def default(self, line):
        "Handle unknown commands"
        self.log_and_print("error", f"[ERROR] Unknown command: {line}. Type 'help' to see the command list.")

    def signal_handler(self, signum, frame):
        self.log_and_print("info", "\n[INFO] Exiting shell...")
        exit(0)

if __name__ == "__main__":
    shell = ProgramShell()
    signal.signal(signal.SIGINT, shell.signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, shell.signal_handler)  # Handle termination signals
    shell.cmdloop()

