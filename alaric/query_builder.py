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
    db = client["database"]
    document: Document = Document(db, "users")

    print(await document.get_all())
    # await document.insert(
    #     {
    #         "data": "Don't post your connection url with the username and password online..."
    #     }
    # )


if __name__ == "__main__":
    asyncio.run(main())
