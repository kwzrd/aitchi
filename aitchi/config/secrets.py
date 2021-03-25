import logging
from os import environ

log = logging.getLogger(__name__)


class _Secrets:
    """Runtime abstraction exposing environment variables."""

    def __init__(self) -> None:
        """Load attributes from environment."""
        log.info("Loading secrets from environment")

        keys = ("BOT_TOKEN", "TIKTOK_ID")
        if any(key not in environ.keys() for key in keys):
            raise Exception(f"Environment lacks required variables: {keys}")

        self.bot_token = str(environ.get("BOT_TOKEN"))  # Discord login token
        self.tiktok_id = int(environ.get("TIKTOK_ID"))  # TikTok application ID


Secrets = _Secrets()
