import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient

from alaric import *
from alaric.comparison import *
from alaric.logical import *
from alaric.meta import *
from alaric.projections import *


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO"])
    db = client["COMPX323"]
    document: Document = Document(db, "movies")

    await document.find_many()


if __name__ == "__main__":
    asyncio.run(main())
