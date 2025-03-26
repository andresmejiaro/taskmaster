import logging
import logging.handlers

logger = logging.getLogger("Taskmaster")
logger.setLevel(logging.DEBUG)
logger.propagate = False

file_handler = logging.FileHandler("taskmaster.log")
file_handler.setLevel(logging.DEBUG)

syshandler = logging.handlers.SysLogHandler(address="/dev/log")
syshandler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler.setFormatter(formatter)
syshandler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(syshandler)
