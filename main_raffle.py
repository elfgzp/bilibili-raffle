#!/usr/bin/env python3

# python lib
import sys
import asyncio
import contextlib

# custom lib
from printer import cprint
from runner import Runner


def cancel_tasks():
    pending = [t for t in asyncio.Task.all_tasks() \
            if not t.done() and t is not asyncio.Task.current_task()]
    [t.cancel() for t in pending]
    return pending


async def shutdown(loop=None):
    loop = loop if loop is not None else asyncio.get_event_loop()
    pending = cancel_tasks()
    cprint(f'Cancelling {len(pending)} tasks...', color='yellow')
    with contextlib.suppress(asyncio.CancelledError):
        await asyncio.gather(*pending, return_exceptions=False)
    await asyncio.sleep(0)


if __name__ == '__main__':
    if sys.version_info < (3,6):
        sys.stderr.write('Please update to Python3.6+\n')
        sys.exit(1)

    loop = asyncio.get_event_loop()
    try:
        with contextlib.suppress(asyncio.CancelledError):
            loop.run_until_complete(Runner(loop=loop).run())
    finally:
        shutdown_task = loop.create_task(shutdown(loop=loop))
        loop.run_until_complete(shutdown_task)
        loop.stop()
        # loop.close()

