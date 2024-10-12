import asyncio
import os
import secrets
from copy import copy
from pprint import pprint
from typing import Dict

from motor.motor_asyncio import AsyncIOMotorClient

from alaric import *
from alaric.encryption import *
from alaric.comparison import *
from alaric.logical import *
from alaric.meta import *
from alaric.projections import *
from alaric.types import *


async def main():
    # client = AsyncIOMotorClient(os.environ["MONGO"])
    # db = client["test_encryption"]

    Negate(Exists("Test"))

    print(AQ(EQ("channel_id", None)).build())


# {'$and': [{'suggestion': {'$regex': 'include these'}, {'state': {'$eq': 'pending'}}]}

if __name__ == "__main__":
    asyncio.run(main())
