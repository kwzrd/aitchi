import logging
import socket
from datetime import datetime

import aiohttp
from discord.ext import commands

from aitchi.config import Env

log = logging.getLogger(__name__)


class Aitchi(commands.Bot):
    """Aitchi."""

    start_time: datetime
    http_session: aiohttp.ClientSession

    def __init__(self) -> None:
        """
        Prepare instance attributes & delegate to superclass.

        All args pass through to super init.
        """
        log.info("Preparing Aitchi instance")

        self.start_time = datetime.utcnow()

        connector = aiohttp.TCPConnector(resolver=aiohttp.AsyncResolver(), family=socket.AF_INET)
        self.http_session = aiohttp.ClientSession(connector=connector)

        super().__init__(command_prefix=Env.prefix)

    async def close(self) -> None:
        """
        Close HTTP session.

        The resource should be released before the event loop closes.
        """
        log.info("Closing Aitchi instance")

        await self.http_session.close()

        await super().close()
