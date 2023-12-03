from fakeredis import aioredis
import pytest
from mongomock_motor import AsyncMongoMockClient

from alaric import Document, Cursor, EncryptedDocument
from alaric.cached_document import CachedDocument
from tests.converter import Converter


@pytest.fixture
async def mocked_mongo():
    return AsyncMongoMockClient()


@pytest.fixture
async def mocked_database(mocked_mongo):
    return mocked_mongo["test"]  # noqa


@pytest.fixture
async def mocked_redis():
    redis = aioredis.FakeRedis()
    await redis.flushdb()  # ensure tests are idempotent
    return redis


@pytest.fixture
async def document(mocked_database) -> Document:
    return Document(mocked_database, "test")


@pytest.fixture
async def encryption_key() -> bytes:
    return EncryptedDocument.generate_aes_key()


@pytest.fixture
async def encrypted_document(mocked_database, encryption_key) -> EncryptedDocument:
    return EncryptedDocument(mocked_database, "test", encryption_key=encryption_key)


@pytest.fixture
async def converter_document(mocked_database) -> Document:
    return Document(mocked_database, "test", converter=Converter)


@pytest.fixture
async def cached_document(document, mocked_redis):
    return CachedDocument(
        document=document,
        redis_client=mocked_redis,
        extra_lookups=[["value"]],
    )


@pytest.fixture
async def cursor(document) -> Cursor:
    return Cursor.from_document(document)
