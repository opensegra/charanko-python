import asyncio


class AsyncPassThrough:
    def __init__(self, max_chunks: int = 16) -> None:
        self._queue: asyncio.Queue[bytes | None] = asyncio.Queue(maxsize=max_chunks)
        self._closed: bool = False
        self._done: asyncio.Future[None] = asyncio.get_running_loop().create_future()

    @property
    def done(self) -> asyncio.Future[None]:
        return self._done

    async def write(self, data: bytes) -> None:
        if self._closed:
            raise RuntimeError("Stream is closed")

        await self._queue.put(data)

    async def read(self) -> bytes:
        chunk = await self._queue.get()

        if chunk is None:
            return b""

        return chunk

    async def close(self) -> None:
        if self._closed:
            return

        self._closed = True
        await self._queue.put(None)

        if not self._done.done():
            self._done.set_result(None)
