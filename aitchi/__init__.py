import logging
from datetime import datetime
from pathlib import Path

# Log file are written here
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Each run will have a distinct log file named using current UTC datetime in ISO format
log_file = Path(log_dir, f"{datetime.utcnow().isoformat()}.log")

# Custom log format
fmt = logging.Formatter(
    fmt="{asctime} | {levelname:.3} | {name} | {message}",
    datefmt="%Y-%m-%d %H:%M:%S",  # Ex: 2021-03-22 21:21:31
    style="{",  # Style arg enables f-string syntax
)

# We'll log both to stdout and to our run file
handle_console = logging.StreamHandler()  # Defaults to stdout
handle_file = logging.FileHandler(log_file, encoding="UTF-8")

# We listen for all levels
root_log = logging.getLogger()
root_log.setLevel(logging.DEBUG)

# Now we register the handlers with the root logger
for handler in (handle_console, handle_file):
    root_log.addHandler(handler)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(fmt)
