import logging
import typing as t

from discord.ext import commands

from aitchi.aitchi import Aitchi
from aitchi.config import Env
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

    async def fetch_videos(self) -> t.Dict[str, t.Any]:
        """
        Poll TikTok API for the last 10 videos from the configured user.

        Raises an exception on non-200 responses. Otherwise, the JSON response is returned as a Python object.
        """
        log.info("Polling API for videos!")

        params = {
            "count": 10,  # How many videos to get
            "cursor": 0,  # Starting from 0th video, i.e. last 10
            "aid": Env.tiktok_aid,  # Application ID
            "secUid": Config.tiktok_user,  # Target user
        }
        async with self.bot.http_session.get("https://m.tiktok.com/api/post/item_list", params=params) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get video list due to status: {resp.status}")
            return await resp.json()


def setup(bot: Aitchi) -> None:
    """Load cog."""
    bot.add_cog(TikTok(bot))
