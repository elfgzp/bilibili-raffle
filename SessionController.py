# python lib
import asyncio
import aiohttp
from typing import Optional


class Session:

    def __init__(self, 
                 loop: Optional[asyncio.AbstractEventLoop] = None, 
                 **kwargs) -> None:
        loop = loop if loop is not None else asyncio.get_event_loop()
        self.loop = loop

        self.session_open_task = self.loop.create_task(self.open_session(**kwargs))
        self.session_open_waiter = self.loop.create_future()
        self.session_keep_alive = self.loop.create_future()

    async def open_session(self, **kwargs):
        async with aiohttp.ClientSession(loop=self.loop, **kwargs) as session:
            self.session_open_waiter.set_result(session)
            await self.session_keep_alive

    async def close_session(self):
        keep_alive = self.session_keep_alive
        keep_alive.done() or keep_alive.set_result(None)
        await self.session_open_task

def new_session(loop=None, **kwargs):
    s = Session(loop=loop, **kwargs)
    return s.session_open_waiter, s
