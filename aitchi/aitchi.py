import logging
import socket

import aiohttp
from discord.ext import commands

log = logging.getLogger(__name__)


class Aitchi(commands.Bot):
    """Aitchi."""

    http_session: aiohttp.ClientSession

    def __init__(self, *args, **kwargs) -> None:
        """
        Prepare instance attributes & delegate to superclass.

        All args pass through to super init.
        """
        log.info("Preparing Aitchi instance")

        connector = aiohttp.TCPConnector(resolver=aiohttp.AsyncResolver(), family=socket.AF_INET)
        self.http_session = aiohttp.ClientSession(connector=connector)

        super().__init__(*args, **kwargs)
