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

# We listen for all levels by default
root_log = logging.getLogger()
root_log.setLevel(logging.DEBUG)

# Now we register the handlers with the root logger
for handler in (handle_console, handle_file):
    root_log.addHandler(handler)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(fmt)

# Bump levels of noisy 3rd party loggers
to_raise = ("asyncio", "discord")
for log_name in to_raise:
    logging.getLogger(log_name).setLevel(logging.WARNING)

log = logging.getLogger(__name__)


def _age(path: Path) -> int:
    """
    Calculate age of log file at `path` in days.

    The creation timestamp is extracted from the ISO filename.
    """
    created_at = datetime.fromisoformat(path.stem)
    difference = datetime.utcnow() - created_at

    return difference.days


def _prune(after_days: int = 30) -> None:
    """Prune existing logs older than `after_days`."""
    log.debug(f"Pruning logs directory (after days: {after_days})")

    eligible = [file for file in log_dir.glob("*.log") if _age(file) > after_days and file != log_file]
    log.debug(f"Removing {len(eligible)} logs")

    for file in eligible:
        file.unlink()


_prune()
