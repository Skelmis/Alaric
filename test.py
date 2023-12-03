import asyncio
import logging
import os
from datetime import timedelta

from motor.motor_asyncio import AsyncIOMotorClient

from alaric import Document
from alaric.cached_document import CachedDocument


class Test:
    def __init__(self, _id, data):
        self.data = data
        self._id = _id

    def as_dict(self):
        return {"_id": self._id, "data": self.data}

    def as_filter(self):
        return {"_id": self._id}

    def __str__(self):
        return f"Test<{self.as_dict()}>"


logging.basicConfig(level=logging.DEBUG)


async def main():
    import redis.asyncio as redis

    client = redis.Redis()
    mongo = AsyncIOMotorClient(os.environ.get("URL"))
    db = mongo["cached_documents_testing"]
    doco = Document(db, "test_collection", converter=Test)
    cd: CachedDocument[Test] = CachedDocument(
        document=doco,
        redis_client=client,
        cache_ttl=timedelta(seconds=1),
        extra_lookups=[["data"]],
    )
    base = Test(1, "hello")
    await cd.set(base, base)
    await asyncio.sleep(2)

    r_1 = await cd.get({"_id": 1})
    print(r_1)  # cache miss
    r_2 = await cd.get({"_id": 1})
    print(r_2)  # cache hit
    await asyncio.sleep(2)
    r_3 = await cd.get({"_id": 1})
    print(r_3)  # cache miss
    r_4: Test = await cd.get({"data": "hello"})
    print(r_4)  # cache hit

    r_4.data = "world"
    await cd.set(r_4, r_4)
    r_5 = await cd.get({"data": "world"})
    print(r_5)  # cache hit
    r_6 = await cd.get({"_id": 1})
    print(r_6)  # cache hit

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
