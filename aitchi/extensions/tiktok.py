import logging
import typing as t

import discord
from discord.ext import commands, tasks

from aitchi.aitchi import Aitchi
from aitchi.config import Config, Secrets
from aitchi.persistence import Store

log = logging.getLogger(__name__)


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

    async def report_error(self, exception: Exception) -> None:
        """
        Send an error report to the configured log channel.

        The `exception` message will be included.
        """
        log.debug(f"Dispatching error report for exception of type: {type(exception)}")

        await self.bot.wait_until_ready()
        log_channel: t.Optional[discord.TextChannel] = self.bot.get_channel(Config.log_channel)

        if log_channel is None:
            log.critical(f"Failed to acquire configured log channel: {Config.log_channel} not found!")
            return

        await log_channel.send(f"TikTok daemon stopped due to exception:\n```{exception}```")

    async def fetch_videos(self) -> t.Dict[str, t.Any]:
        """
        Poll TikTok API for the last 10 videos from the configured user.

        Raises an exception on non-200 responses. Otherwise, the JSON response is returned as a Python object.
        """
        log.debug("Polling TikTok API for recent videos!")

        params = {
            "count": 10,  # How many videos to get
            "cursor": 0,  # Starting from 0th video, i.e. last 10
            "aid": Secrets.tiktok_id,  # Application ID
            "secUid": Config.tiktok_target,  # Target user
        }
        async with self.bot.http_session.get("https://m.tiktok.com/api/post/item_list", params=params) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get video list due to status: {resp.status}")
            return await resp.json()

    async def daemon_main(self) -> None:
        """
        Check for previously unseen videos and notify the configured channel.

        This function is implemented naively. An unexpected response from the API will cause an exception to propagate
        to the caller.

        We depend on the persistence module to remember already seen videos. In the case that the store is empty,
        we populate it with the current videos. This indicates the maiden case and requires special behaviour to
        avoid sending notifications retroactively.
        """
        log.debug("Daemon main: fetching video list")

        resp = await self.fetch_videos()

        recent_videos = [int(video["id"]) for video in resp["itemList"]]
        seen_videos = self.store.get("seen_videos")

        if seen_videos is None:
            log.debug("Daemon main: store is empty, caching recent videos (maiden case)")
            self.store.set("seen_videos", recent_videos)
            return

        new_videos = [video for video in recent_videos if video not in seen_videos]

        if not new_videos:
            log.debug("Daemon main: found no unseen videos")
            return

        log.debug(f"Found {len(new_videos)} new videos!")

        await self.bot.wait_until_ready()  # Ensure cache is ready before we grab the channel
        notification_channel: t.Optional[discord.TextChannel] = self.bot.get_channel(Config.notification_channel)

        if notification_channel is None:
            raise Exception(f"Failed to acquire configured notification channel: {Config.notification_channel}")

        log.debug(f"Sending notifications to: #{notification_channel.name}")

        for new_video in new_videos:
            tiktok_url = f"https://www.tiktok.com/@charlixcx/video/{new_video}"
            await notification_channel.send(f"New TikTok: {tiktok_url}")

        log.debug("Caching new videos")
        self.store.set("seen_videos", seen_videos + recent_videos)

    @tasks.loop(minutes=10)
    async def daemon(self) -> None:
        """
        Periodically call `daemon_main`.

        If an exception propagates out of the main, the daemon will send an alert to the configured log channel
        and stop itself. This will generally happen if the API returns an unexpected response.
        """
        log.info("Daemon: invoking main")

        try:
            await self.daemon_main()
        except Exception as exc:
            log.error("Daemon encountered an unhandled exception and will stop!", exc_info=exc)
            self.daemon.stop()
            await self.report_error(exc)
        else:
            log.debug("Daemon pass complete")


def setup(bot: Aitchi) -> None:
    """Load cog."""
    bot.add_cog(TikTok(bot))
