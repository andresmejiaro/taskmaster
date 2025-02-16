import cmd
import signal

class ProgramShell(cmd.Cmd):
    prompt = "taskmaster> "

    def do_status(self, arg):
        "Show the status of all programs"
        print("[INFO] Fetching status of all programs...")

    def do_start(self, arg):
        "Start a specific program: start <program_name>"
        if not arg:
            print("[ERROR] Please specify a program to start.")
        else:
            print(f"[INFO] Would run: start {arg}")

    def do_stop(self, arg):
        "Stop a specific program: stop <program_name>"
        if not arg:
            print("[ERROR] Please specify a program to stop.")
        else:
            print(f"[INFO] Would run: stop {arg}")

    def do_restart(self, arg):
        "Restart a specific program: restart <program_name>"
        if not arg:
            print("[ERROR] Please specify a program to restart.")
        else:
            print(f"[INFO] Would run: restart {arg}")

    def do_reload(self, arg):
        "Reload the configuration file"
        print("[INFO] Reloading configuration file...")

    def do_exit(self, arg):
        "Exit the shell"
        print("[INFO] Exiting shell...")
        return True
    
    def do_EOF(self, arg):
        "Handle Ctrl+D (EOF) to exit the shell"
        print("\n[INFO] Exiting shell...")
        return True

    def default(self, line):
        "Handle unknown commands"
        print(f"[ERROR] Unknown command: {line}. Type 'help' to see the command list.")

    def signal_handler(self, signum, frame):
        print("\n[INFO] Exiting shell...")
        exit(0)

if __name__ == "__main__":
    shell = ProgramShell()
    signal.signal(signal.SIGINT, shell.signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, shell.signal_handler)  # Handle termination signals
    shell.cmdloop()
