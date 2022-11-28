from alaric import Document
from alaric.meta import All


async def test_all(document: Document):
    await document.bulk_insert([{"number": i} for i in range(10)])

    r_1 = await document.find_many(All())
    assert len(r_1) == 10
