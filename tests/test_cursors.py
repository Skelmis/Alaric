import pytest

import alaric
from alaric import AQ, Document, Cursor
from alaric.comparison import IN, EQ
from alaric.logical import AND
from alaric.projections import Projection, Show, Hide
from tests.converter import Converter


async def test_set_filter(cursor: Cursor):
    assert cursor._filter == {}

    cursor.set_filter({"_id": 1})
    assert cursor._filter == {"_id": 1}

    cursor.set_filter(AQ(IN("prefix", ["!", "?"])))
    assert cursor._filter == {"prefix": {"$in": ["!", "?"]}}

    cursor.set_filter(AQ(AND(IN("prefix", ["!", "?"]), EQ("activated_premium", True))))
    assert cursor._filter == {
        "$and": [
            {"prefix": {"$in": ["!", "?"]}},
            {"activated_premium": {"$eq": True}},
        ]
    }

    cursor.set_filter()
    assert cursor._filter == {}

    cursor.set_filter(Converter(1, 2))
    assert cursor._filter == {"_id": 1}


async def test_set_projections(cursor: Cursor):
    assert cursor._projections is None

    cursor.set_projections({"_id": 1})
    assert cursor._projections == {"_id": 1}

    cursor.set_projections({"data": 1})
    assert cursor._projections == {"data": 1}

    cursor.set_projections(Projection(Show("data")))
    assert cursor._projections == {"data": 1, "_id": 0}

    cursor.set_projections(Projection(Show("data"), Show("_id")))
    assert cursor._projections == {"data": 1, "_id": 1}


async def test_set_limit(cursor: Cursor):
    assert cursor._limit == 0

    cursor.set_limit(1)
    assert cursor._limit == 1

    with pytest.raises(ValueError):
        cursor.set_limit(-1)


async def test_set_sort(cursor: Cursor):
    with pytest.raises(ValueError):
        cursor.set_sort({})

    with pytest.raises(ValueError):
        cursor.set_sort(1)

    assert cursor._sort is None

    cursor.set_sort(("count", alaric.Descending))
    assert cursor._sort == [("count", -1)]

    cursor.set_sort([("count", alaric.Ascending), ("backup_count", alaric.Descending)])
    assert cursor._sort == [("count", 1), ("backup_count", -1)]

    cursor.set_sort()
    assert cursor._sort is None


async def test_async_for(document: Document):
    cursor: Cursor = Cursor.from_document(document)
    await document.bulk_insert([{"data": i} for i in range(10)])

    count = 0
    async for _ in cursor:
        count += 1

    assert count == 10


async def test_execute(document: Document):
    cursor: Cursor = Cursor.from_document(document)
    await document.bulk_insert([{"data": i} for i in range(10)])

    r_1 = await cursor.execute()
    assert isinstance(r_1, list)
    assert len(r_1) == 10


async def test_limit(document: Document):
    cursor: Cursor = Cursor.from_document(document).set_limit(5)
    await document.bulk_insert([{"data": i} for i in range(10)])

    r_1 = await cursor.execute()
    assert isinstance(r_1, list)
    assert len(r_1) == 5


async def test_projections(document: Document):
    cursor: Cursor = (
        Cursor.from_document(document)
        .set_projections(Projection(Hide("_id"), Show("data")))
        .set_limit(1)
    )
    await document.bulk_insert([{"data": i} for i in range(10)])

    r_1 = await cursor.execute()
    assert isinstance(r_1, list)

    data = r_1[0]
    assert data == {"data": 0}


async def test_sort(document: Document):
    cursor: Cursor = (
        Cursor.from_document(document)
        .set_projections(Projection(Hide("_id"), Show("data")))
        .set_limit(1)
        .set_sort(("data", alaric.Descending))
    )
    await document.bulk_insert([{"data": i} for i in range(10)])

    r_1 = await cursor.execute()
    assert isinstance(r_1, list)

    data = r_1[0]
    assert data == {"data": 9}


async def test_converter_from_document(converter_document: Document):
    cursor: Cursor = Cursor.from_document(converter_document)
    await converter_document.bulk_insert([{"value": i} for i in range(10)])

    r_1 = await cursor.execute()
    assert isinstance(r_1, list)
    assert len(r_1) == 10
    assert isinstance(r_1[0], Converter)


async def test_converter_create_cursor(converter_document: Document):
    cursor: Cursor = converter_document.create_cursor()
    await converter_document.bulk_insert([{"value": i} for i in range(10)])

    r_1 = await cursor.execute()
    assert isinstance(r_1, list)
    assert len(r_1) == 10
    assert isinstance(r_1[0], Converter)
