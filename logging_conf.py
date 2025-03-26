import logging

logger = logging.getLogger("Taskmaster")

console_hander = logging.FileHandler("taskmaster.log")
syshandlet = logging.handlers.SysLogHandler(address="/dev/log")