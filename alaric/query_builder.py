import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient

from alaric import *
from alaric.comparison import *
from alaric.logical import *
from alaric.meta import *


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO"])
    db = client["alaric_testing"]
    document: Document = Document(db, "test")

    # await document.insert({"key": "one", "data": "test", "list": [1, 2, 3]})
    # await document.insert({"key": "two", "data": "test", "list": [1, 2, 3]})

    r_1 = await document.find(EXISTS("key"))
    print(r_1)

    r_2 = await document.find({"key": "one"})
    print(r_2)

    r_3 = await document.find(AND(EQ("key", "one"), EQ("data", "test")))
    print(r_3)

    r_4 = await document.find_many_by_custom(IN("key", ["one", "three"]))
    print(r_4)

    r_5 = await document.find_many_by_custom(NEGATE(IN("key", ["one", "three"])))
    print(r_5)

    r_6 = await document.find_many_by_custom(
        AND(
            OR(
                EQ("key", "one"),
                EQ("key", "two"),
            ),
            AND(EQ("data", "test"), EXISTS("list")),
        )
    )
    print(r_6)


if __name__ == "__main__":
    asyncio.run(main())
