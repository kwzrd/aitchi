import logging

from discord.ext import commands

from aitchi.aitchi import Aitchi
from aitchi.persistence import Store

log = logging.getLogger(__name__)


class Config:
    """Extension configuration."""

    tiktok_user = "MS4wLjABAAAAok8FiOPFZg5o8vKv-oxSwYuM-gbhKldv_1_nnPAZQ1XdqeTJkUcuoz6SAjSdzcmr"
    notification_channel = 733635779603070998


class TikTok(commands.Cog):
    """TikTok notifications."""

    def __init__(self, bot: Aitchi) -> None:
        """Initialise store."""
        self.bot = bot
        self.store = Store(namespace="tiktok")


def setup(bot: Aitchi) -> None:
    """Load cog."""
    bot.add_cog(TikTok(bot))
