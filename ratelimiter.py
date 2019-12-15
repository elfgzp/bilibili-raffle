# python lib
import asyncio
import time

class RateLimiter:

    '''
    Limit the number of requests sent in a time period
    ``RATE``  :=  requests per second
    ``MAX_TOKENS``  :=  requests pool
    '''

    RATE = 15
    MAX_TOKENS = 20

    def __init__(self, client):
        self.client = client
        self.tokens = RateLimiter.MAX_TOKENS
        self.updated_at = time.monotonic()

    async def get(self, *args, **kwargs):
        await self.wait_for_token()
        now = time.monotonic()
        response = await self.client.get(*args, **kwargs)
        return response

    async def post(self, *args, **kwargs):
        await self.wait_for_token()
        now = time.monotonic()
        response = await self.client.post(*args, **kwargs)
        return response

    async def wait_for_token(self):
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.RATE
        if new_tokens + self.tokens >= 1:
            self.tokens = min(new_tokens + self.tokens, self.MAX_TOKENS)
            self.updated_at = now


