import pytest

from alaric import Document
from alaric.projections import Projection, Show
from tests.converter import Converter


async def test_find_missing(document: Document):
    r_1 = await document.find({})
    assert r_1 is None


async def test_find_broad_query(document: Document):
    await document.insert({"_id": "one"})

    r_1 = await document.find({})
    assert r_1 is not None
    assert r_1["_id"] == "one"


async def test_find_specific(document: Document):
    await document.insert({"_id": "one"})

    r_1 = await document.find({"_id": "two"})
    assert r_1 is None

    r_2 = await document.find({"_id": "one"})
    assert r_2 is not None
    assert r_2["_id"] == "one"


async def test_find_converter_missing(converter_document: Document):
    r_1 = await converter_document.find({})
    assert r_1 is None


async def test_find_converter_with_missing_fields(converter_document: Document):
    await converter_document.insert({"_id": "one"})

    r_1 = await converter_document.find({"_id": "one"})
    assert r_1 is not None
    assert isinstance(r_1, Converter)
    assert r_1.id == "one"
    assert r_1.value is None


async def test_find_converter_full_fields(converter_document: Document):
    await converter_document.insert({"_id": "one", "value": "test"})

    r_1 = await converter_document.find({"_id": "one"})
    assert r_1 is not None
    assert isinstance(r_1, Converter)
    assert r_1.id == "one"
    assert r_1.value == "test"


async def test_find_converter_with_extra_fields(converter_document: Document):
    await converter_document.insert(
        {"_id": "one", "value": "test", "value_two": "test two"}
    )

    with pytest.raises(TypeError):
        await converter_document.find({"_id": "one"})


async def test_converter_with_projections(converter_document: Document):
    await converter_document.insert({"_id": "one", "value": "test"})
    r_1 = await converter_document.find({"_id": "one"})
    assert r_1 is not None
    assert isinstance(r_1, Converter)
    assert r_1.id == "one"
    assert r_1.value == "test"

    r_2 = await converter_document.find(
        {"_id": "one"}, projections=Projection(Show("_id"))
    )
    assert r_2 is not None
    assert isinstance(r_2, Converter)
    assert r_2.id == "one"
    assert r_2.value is None


async def test_find_try_convert(converter_document: Document):
    await converter_document.insert({"_id": "one", "value": "test"})

    r_1 = await converter_document.find({"_id": "one"}, try_convert=False)
    assert r_1 is not None
    assert not isinstance(r_1, Converter)

    r_2 = await converter_document.find({"_id": "one"})
    assert r_2 is not None
    assert isinstance(r_2, Converter)


async def test_find_filterable(document: Document):
    obj = Converter("test")

    r_1 = await document.find(obj)
    assert r_1 is None

    await document.insert({"_id": "test"})
    r_2 = await document.find(obj)
    assert r_2 is not None
