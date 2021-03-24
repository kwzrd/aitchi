import logging

from discord.ext import commands

from aitchi.aitchi import Aitchi

log = logging.getLogger(__name__)


class TikTok(commands.Cog):
    """TikTok notifications."""

    def __init__(self, bot: Aitchi) -> None:
        self.bot = bot


def setup(bot: Aitchi) -> None:
    """Load cog."""
    bot.add_cog(TikTok(bot))
