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

    r_1 = await document.get_all(projections=PROJECTION(HIDE("director", "_id")))
    print(r_1)


if __name__ == "__main__":
    asyncio.run(main())
