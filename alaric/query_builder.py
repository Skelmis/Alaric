import asyncio
import os
import secrets

from motor.motor_asyncio import AsyncIOMotorClient

from alaric import *
from alaric.comparison import *
from alaric.logical import *
from alaric.meta import *
from alaric.projections import *
from alaric.types import *


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO"])
    db = client["COMPX323"]
    document: Document = Document(db, "movies")

    # r_1 = await document.find(EQ("_id", ObjectId("6297cf0186d144fe9b619135")))
    # print(r_1)
    print(AQ(IN("state", ["approved", "rejected"])).build())


if __name__ == "__main__":
    asyncio.run(main())
