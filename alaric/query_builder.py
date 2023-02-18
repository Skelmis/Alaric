import asyncio
import os
import secrets
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
    client = AsyncIOMotorClient(os.environ["MONGO"])
    db = client["test_encryption"]
    # key = EncryptedDocument.generate_aes_key()
    key = bytes.fromhex(os.environ["AES_KEY"])
    document: EncryptedDocument = EncryptedDocument(
        db,
        "movies",
        encryption_key=key,
        hashed_fields=HashedFields("two"),
        encrypted_fields=EncryptedFields("test"),
    )
    await document.insert({"test": {"ngl": 1}, "two": 1, "three": "raw data"})
    r_1: Dict = await document.find(AQ(HashedQueryField(EQ("two", 1))))
    current_hash = r_1["two"]
    r_1["three"] = "data"
    await document.update(
        AQ(HashedQueryField(EQ("two", 1))), r_1, ignore_fields=IgnoreFields("two")
    )
    r_2: Dict = await document.find(AQ(HashedQueryField(EQ("two", 1))))
    print(current_hash == r_2["two"])


if __name__ == "__main__":
    asyncio.run(main())
