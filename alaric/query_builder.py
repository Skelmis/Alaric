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
    # key = EncryptedDocument.generate_aes_key()
    # print(key)
    # enc = EncryptedDocument(
    #     db,
    #     "movies",
    #     encryption_key=key,
    #     automatic_hashed_fields=AutomaticHashedFields("test"),
    #     encrypt_all_fields=True,
    # )
    #
    # await enc.insert({"test": True, "data": "ello"})
    #
    # r_1 = await enc.find(AQ(HQF(EQ("test_hashed", True))))
    # print(r_1)

    print(AQ(EXISTS("image_url")).build())


if __name__ == "__main__":
    asyncio.run(main())
