import asyncio


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self.is_alive = False
        self._task = None

    def start(self, *args, **kwargs):
        self.is_alive = True
        self._task = asyncio.create_task(self._job(*args, **kwargs))

    async def _job(self, *args, **kwargs):
        await asyncio.sleep(self._timeout)
        await self._callback(*args, **kwargs)
        self.is_alive = False

    def cancel(self):
        self._task.cancel()
        self.is_alive = False
