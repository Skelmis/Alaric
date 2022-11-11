import pytest
from mongomock_motor import AsyncMongoMockClient

from alaric import Document
from tests.converter import Converter


@pytest.fixture
async def mocked_mongo():
    return AsyncMongoMockClient()


@pytest.fixture
async def mocked_database(mocked_mongo):
    return mocked_mongo["test"]  # noqa


@pytest.fixture
async def document(mocked_database) -> Document:
    return Document(mocked_database, "test")


@pytest.fixture
async def converter_document(mocked_database) -> Document:
    return Document(mocked_database, "test", converter=Converter)
