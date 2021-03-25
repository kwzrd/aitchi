import json
import logging
from enum import Enum
from pathlib import Path

log = logging.getLogger(__name__)


class Environment(Enum):
    PRODUCTION = "Production"
    DEVELOPMENT = "Development"


class _Config:
    """
    Runtime abstraction exposing JSON configuration.

    We check for the configuration file in the 'environments' directory in the following order:

    1. 'development.json'
    2. 'production.json'

    The first found file is used.
    """

    environment: Environment  # The environment we're currently in

    bot_prefix: str  # Command prefix

    notification_channel: int  # Send new TikTok notifications here
    log_channel: int  # Send important application logs here

    tiktok_target: str  # Target TikTok user ID

    def __init__(self, load_from: Path) -> None:
        """Load attributes from JSON file at `load_from`."""
        log.info(f"Loading config from: {load_from}")

        as_text = load_from.read_text(encoding="UTF-8")
        cfg = json.loads(as_text)

        missing = []

        for attribute in self.__annotations__:
            if attribute in cfg:
                setattr(self, attribute, cfg[attribute])
            else:
                missing.append(attribute)

        if missing:
            raise Exception(f"Config attributes not found in source file: {missing}")

        self.environment = Environment(self.environment)


environments_directory = Path("aitchi", "config", "environments")

for source_option in ("development.json", "production.json"):
    source = Path(environments_directory, source_option)
    if source.exists():
        Config = _Config(load_from=source)
        break
else:
    raise Exception("No config source file found!")
