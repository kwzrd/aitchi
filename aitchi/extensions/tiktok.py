import logging
import typing as t

import discord
from discord.ext import commands, tasks

from aitchi.aitchi import Aitchi
from aitchi.config import Config, Secrets
from aitchi.persistence import Store

log = logging.getLogger(__name__)


def deep_lookup(mapping: t.Mapping, path: t.Iterable[t.Hashable]) -> t.Any:
    """Fetch value at `path` in `mapping`."""
    value = mapping
    for item in path:
        value = value[item]
    return value


class TikTokVideo:
    """Remote video representation."""

    id: t.Annotated[str, "video", "id"]

    def __init__(self, dictionary: dict[str, t.Any]) -> None:
        """Initialise instance from `dictionary`."""
        for attr_name, annotation in self.__annotations__.items():
            value = deep_lookup(dictionary, annotation.__metadata__)
            setattr(self, attr_name, value)


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

    async def fetch_videos(self) -> list[TikTokVideo]:
        """
        Poll TikTok API for the last 10 videos from the configured user.

        Raise exception on non-200 responses, or when the response lacks expected keys.
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

            log.debug("Fetch successful, parsing JSON response")
            payload = await resp.json()

        return [TikTokVideo(item) for item in payload["itemList"]]

    async def daemon_main(self) -> None:
        """
        Check for previously unseen videos and notify the configured channel.

        Propagate exceptions in unexpected cases. The caller is responsible for error handling.
        """
        log.debug("Daemon main: fetching video list")

        recent_videos = await self.fetch_videos()
        seen_video_ids: list[str] = self.store.get("seen_videos")

        if seen_video_ids is None:
            log.debug("Daemon main: store is empty, caching recent videos (maiden case)")
            self.store.set("seen_videos", [video.id for video in recent_videos])
            return

        new_videos = [video for video in recent_videos if video.id not in seen_video_ids]

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
            tiktok_url = f"https://www.tiktok.com/@charlixcx/video/{new_video.id}"
            await notification_channel.send(f"New TikTok: {tiktok_url}")

        log.debug("Caching new videos")
        self.store.set("seen_videos", seen_video_ids + [video.id for video in new_videos])

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
