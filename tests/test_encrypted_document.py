import pytest

from alaric import Document, EncryptedDocument, AQ, util
from alaric.comparison import EQ
from alaric.projections import Projection, Show
from tests.converter import Converter
from alaric.encryption import *


# This test suite assumes all of the base document tests pass


async def test_no_encrypt(encrypted_document: EncryptedDocument):
    await encrypted_document.insert({"data": 1})
    r_1 = await encrypted_document.find({"data": 1})
    assert r_1 is not None


async def test_basic_field_encryption(encrypted_document: EncryptedDocument):
    encrypted_document._encrypted_fields = EncryptedFields("data")
    await encrypted_document.insert({"data": 1})

    r_1 = await encrypted_document.find({"data": 1})
    assert r_1 is None, "Shouldn't be able to query encrypted fields for data correctly"


async def test_basic_field_hashing(encrypted_document: EncryptedDocument):
    encrypted_document._hashed_fields = HashedFields("data")
    await encrypted_document.insert({"data": 1})

    r_1 = await encrypted_document.find(AQ(HQF(EQ("data", 1))))
    assert r_1 is not None

    r_2 = await encrypted_document.find(AQ(EQ("data", 1)))
    assert r_2 is None, "Shouldn't be able to query hashed field with raw value"


async def test_incorrect_key(encrypted_document: EncryptedDocument):
    encrypted_document._encrypted_fields = EncryptedFields("data")
    await encrypted_document.insert({"data": 1, "id": 1})
    encrypted_document._encryption_key = EncryptedDocument.generate_aes_key()

    with pytest.raises(ValueError):
        await encrypted_document.find(AQ(EQ("id", 1)))


async def test_automatic_hashed_fields(encrypted_document: EncryptedDocument):
    encrypted_document._automatic_hashed_fields = AutomaticHashedFields("data")

    await encrypted_document.insert({"data": 1})

    r_1 = await encrypted_document.find(AQ(HQF(EQ("data_hashed", 1))))
    assert r_1 is not None
    assert "data_hashed" not in r_1
    assert r_1["data"] == 1

    r_2 = await encrypted_document.find(AQ(HQF(EQ("data", 1))))
    assert r_2 is None


async def test_automatic_hash_with_full_encryption(
    encrypted_document: EncryptedDocument,
):
    encrypted_document._encrypt_all_fields = True
    encrypted_document._automatic_hashed_fields = AutomaticHashedFields("data")

    await encrypted_document.insert({"data": 1})

    r_1 = await encrypted_document.find(AQ(HQF(EQ("data_hashed", 1))))
    assert r_1 is not None
    assert "data_hashed" not in r_1
    assert r_1["data"] == 1

    r_2 = await encrypted_document.find(AQ(HQF(EQ("data", 1))))
    assert r_2 is None

    r_3 = await encrypted_document.find(AQ(EQ("data", 1)))
    assert r_3 is None


async def test_automatic_hash_with_field_encryption(
    encrypted_document: EncryptedDocument,
):
    encrypted_document._encrypted_fields = EncryptedFields("data")
    encrypted_document._automatic_hashed_fields = AutomaticHashedFields("data")

    await encrypted_document.insert({"data": 1})

    r_1 = await encrypted_document.find(AQ(HQF(EQ("data_hashed", 1))))
    assert r_1 is not None
    assert "data_hashed" not in r_1
    assert r_1["data"] == 1

    r_2 = await encrypted_document.find(AQ(HQF(EQ("data", 1))))
    assert r_2 is None

    r_3 = await encrypted_document.find(AQ(EQ("data", 1)))
    assert r_3 is None


async def test_convertors(encrypted_document: EncryptedDocument):
    encrypted_document._encrypt_all_fields = True
    encrypted_document._automatic_hashed_fields = AutomaticHashedFields("id")

    class Test:
        def __init__(self, data, id, _id=None):
            self.data = data
            self.id = id
            self._id = _id

        def as_dict(self):
            return {"data": self.data, "id": self.id}

        def as_filter(self):
            return {"id_hashed": util.hash_field("id", self.id)}

    encrypted_document.converter = Test

    await encrypted_document.insert(Test("hello", 1))

    r_1 = await encrypted_document.find(HQF(EQ("id_hashed", 1)))
    assert r_1 is not None
    assert isinstance(r_1, Test)
    assert r_1.data == "hello"
    assert r_1.id == 1

    r_1.data = "world"
    await encrypted_document.update(r_1, r_1)

    r_2 = await encrypted_document.find(HQF(EQ("id_hashed", 1)))
    assert r_2 is not None
    assert isinstance(r_2, Test)
    assert r_2.data == "world"
