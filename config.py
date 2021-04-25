import logging
from datetime import datetime

LOG_FILENAME = "adclicker.log"

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(LOG_FILENAME, mode="a", encoding="utf-8")
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
log_format = "%(asctime)s [%(levelname)5s] %(lineno)3d: %(message)s"
formatter = logging.Formatter(log_format, datefmt="%d-%m-%Y %H:%M:%S")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

