import logging
import typing as t

from discord.ext import commands, tasks

from aitchi.aitchi import Aitchi
from aitchi.config import Env
from aitchi.persistence import Store

log = logging.getLogger(__name__)


class Config:
    """Extension configuration."""

    tiktok_user = "MS4wLjABAAAAok8FiOPFZg5o8vKv-oxSwYuM-gbhKldv_1_nnPAZQ1XdqeTJkUcuoz6SAjSdzcmr"
    notification_channel = 733635779603070998


class TikTok(commands.Cog):
    """
    TikTok notifications.

    This extension is responsible for polling TikTok for new videos from the configured user. When a new video
    is found, a notification is sent to the configured channel.
    """

    def __init__(self, bot: Aitchi) -> None:
        """Initialise store & start daemon."""
        self.bot = bot
        self.store = Store(namespace="tiktok")

        self.daemon.start()

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

    async def get_new_videos(self) -> t.List[int]:
        """
        Get a list of previously unseen video IDs.

        First we poll the API for the last 10 videos. Any IDs present in the response but not present in the
        persistent store will be persisted for later and returned. This means that this function will only
        return each video ID exactly once.

        In the case that the persistent store is completely empty, we init it with the current 10 videos
        and return an empty list. This will only happen in the maiden case.
        """
        log.info("Getting new videos!")

        try:
            resp = await self.fetch_videos()
        except Exception as fetch_exc:
            log.error("Failed to fetch videos!", exc_info=fetch_exc)
            return []

        log.debug("Videos fetched, checking for attributes")

        try:
            video_ids = [int(video["id"]) for video in resp["itemList"]]
        except KeyError as lookup_exc:
            log.error("Missing attribute in response!", exc_info=lookup_exc)
            return []

        seen_videos = self.store.get("seen_videos", [])
        log.debug(f"Fetched {len(video_ids)} videos, comparing against {len(seen_videos)} videos from store")

        if len(seen_videos) == 0:
            log.debug("Maiden case: initialising store with response")
            self.store.set("seen_videos", video_ids)
            return []

        new_videos = [video_id for video_id in video_ids if video_id not in seen_videos]
        log.debug(f"Found {len(new_videos)} new videos")

        self.store.set("seen_videos", seen_videos + new_videos)

        return new_videos

    @tasks.loop(minutes=5)
    async def daemon(self) -> None:
        """
        Periodically fetch new videos and send them to the configured channel.

        This function orchestrates the extension.
        """
        log.info("Daemon awakens: checking for new videos")

        new_videos = await self.get_new_videos()

        if not new_videos:
            log.debug("Daemon pass complete: no new videos")
            return

        log.info("New videos found, sending notification")

        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(733635779603070998)

        if channel is None:
            log.warning("Cannot send notification, target channel not found!")
            return

        for video_id in new_videos:
            tiktok_url = f"https://www.tiktok.com/@charlixcx/video/{video_id}"
            await channel.send(f"New TikTok: {tiktok_url}")

        log.debug("Daemon pass complete: notifications sent")


def setup(bot: Aitchi) -> None:
    """Load cog."""
    bot.add_cog(TikTok(bot))
