import datetime
import logging
import secrets
from typing import List, Dict, Optional, Union, Any, Type, TYPE_CHECKING

import bson
import orjson
from Crypto.Cipher import AES
from bson import ObjectId
from pymongo.results import DeleteResult
from motor.motor_asyncio import AsyncIOMotorDatabase

from alaric import Document, util
from alaric.abc import Buildable, Filterable, Saveable
from alaric.encryption import (
    EncryptedFields,
    HashedFields,
    IgnoreFields,
    AutomaticHashedFields,
)
from alaric.projections import Projection, Show
from alaric.document import T

log = logging.getLogger(__name__)


# noinspection DuplicatedCode
class EncryptedDocument(Document):
    _version = 1

    def __init__(
        self,
        database: AsyncIOMotorDatabase,
        document_name: str,
        *,
        encryption_key: bytes,
        hashed_fields: Optional[HashedFields] = None,
        automatic_hashed_fields: Optional[AutomaticHashedFields] = None,
        encrypted_fields: Optional[EncryptedFields] = None,
        converter: Optional[Type[T]] = None,
        encrypt_all_fields: bool = False,
    ):
        """
        Parameters
        ----------
        database: AsyncIOMotorDatabase
            The database we are connected to
        document_name: str
            What this collection should be called
        encryption_key: bytes
            The key to use for AES encryption
        hashed_fields: Optional[HashedFields]
            A list of fields to SHA512 hash when encountered
        automatic_hashed_fields: Optional[AutomaticHashedFields]
            A list of fields to create an additional column in
            the db for with a hashed variant without exposing
            the hashed data to the end user.
        encrypted_fields: Optional[EncryptedFields]
            A list of fields to AES encrypt when encountered
        converter: Optional[Type[:py:class:`~alaric.document.T`]]
            An optional class to try
            to convert all data-types which
            return either Dict or List into
        encrypt_all_fields: bool
            If set to True, encrypt all fields regardless of
            `hashed_fields` and `encrypted_fields` options.

            This option respects ignored fields.


        .. code-block:: python
            :linenos:

            from motor.motor_asyncio import AsyncIOMotorClient

            client = AsyncIOMotorClient(connection_url)
            database = client["my_database"]
            config_document = Document(database, "config")
        """
        super().__init__(database, document_name, converter=converter)
        self._encryption_key = encryption_key
        self._hashed_fields: HashedFields = (
            hashed_fields if hashed_fields is not None else HashedFields()
        )
        self._automatic_hashed_fields: AutomaticHashedFields = (
            automatic_hashed_fields
            if automatic_hashed_fields is not None
            else AutomaticHashedFields()
        )
        self._encrypted_fields: EncryptedFields = (
            encrypted_fields if encrypted_fields is not None else EncryptedFields()
        )
        self._encrypt_all_fields: bool = encrypt_all_fields

    def __repr__(self):
        return f"<Document(document_name={self._document_name})>"

    @classmethod
    def generate_aes_key(cls) -> bytes:
        """Generate a valid AES key for usage with this class.

        The output should be stored in an environment variable
        for future usage as otherwise you will lose your data.

        For storage purposes, you may find the following methods useful:
         - bytes.hex()
         - bytes.fromhex()

        Returns
        -------
        bytes
            A valid AES key
        """
        # 256 bit
        return secrets.token_bytes(32)

    def _encrypt_data(self, data: Dict, *, ignore_fields: IgnoreFields) -> Dict:
        encrypted_fields = {}
        for k, v in data.items():
            if k in ignore_fields:
                encrypted_fields[k] = v
                continue

            if k in self._automatic_hashed_fields:
                new_key = f"{k}_hashed"
                if new_key in encrypted_fields or new_key in data:
                    raise ValueError(
                        f"Cannot automatically hash {k} as the column {new_key} already exists in the dataset."
                    )

                encrypted_fields[new_key] = util.hash_field(new_key, v)

            if self._encrypt_all_fields:
                v = self._aes_encrypt_field(v)

            elif k in self._encrypted_fields:
                v = self._aes_encrypt_field(v)

            elif k in self._hashed_fields:
                v = util.hash_field(k, v)

            encrypted_fields[k] = v
        return encrypted_fields

    def _decrypt_data(self, data: Dict) -> Dict:
        # Keep the cursor mirror up to date
        decrypted_fields = {}
        # preprocess out automatic hashed fields
        for ktr in [f"{k}_hashed" for k in self._automatic_hashed_fields]:
            data.pop(ktr, None)

        for k, v in data.items():
            if k in self._encrypted_fields or self._encrypt_all_fields:
                try:
                    if not isinstance(v, bson.ObjectId):
                        v = self._aes_decrypt_field(bytes.fromhex(v))
                except ValueError:
                    raise ValueError("Invalid encryption_key in use for this data.")

            decrypted_fields[k] = v

        return decrypted_fields

    def _aes_encrypt_field(self, value) -> Union[str, ObjectId]:
        # Data is stored in the format b'nonce(16 bytes)tag(16 bytes)ciphertext(remaining)'
        cipher = AES.new(self._encryption_key, AES.MODE_GCM)
        if isinstance(value, str):
            value = f"str     |{value}"
        elif isinstance(value, bool):
            value = f"bool    |{1 if value else 0}"
        elif isinstance(value, int):
            value = f"int     |{value}"
        elif isinstance(value, float):
            value = f"float   |{value}"
        elif isinstance(value, datetime.datetime):
            value = f"datetime|{value.isoformat()}"
        elif isinstance(value, list):
            pre = {"list": value}
            value = f"list    |{orjson.dumps(pre).hex()}"
        elif isinstance(value, dict):
            value = f"dict    |{orjson.dumps(value).hex()}"
        elif isinstance(value, ObjectId):
            log.debug("You asked me to encrypt an ObjectId instance, I can't do that.")
            return value
        else:
            raise ValueError(
                f"{value.__class__.__name__} is not yet supported for encryption"
            )

        if not isinstance(value, bytes):
            value = bytes(value, "utf-8")

        ciphertext, tag = cipher.encrypt_and_digest(value)
        ba = bytearray(cipher.nonce)
        ba.extend(tag)
        ba.extend(ciphertext)
        return ba.hex()

    def _aes_decrypt_field(self, value: bytes):
        # Keep the cursor mirror up to date
        # We assume by here it's an AES field
        def extract_list(data) -> List:
            inner = orjson.loads(bytes.fromhex(data))
            return inner["list"]

        def extract_dict(data):
            return orjson.loads(bytes.fromhex(data))

        def extract_bool(data):
            return True if data == "1" else False

        # Whitelist types
        mappings = {
            "str": str,
            "int": int,
            "float": float,
            "bool": extract_bool,
            "dict": extract_dict,
            "list": extract_list,
            "datetime": datetime.datetime.fromisoformat,
        }
        nonce = value[:16]
        tag = value[16:32]
        ciphertext = value[32:]
        cipher = AES.new(self._encryption_key, AES.MODE_GCM, nonce)
        text = cipher.decrypt_and_verify(ciphertext, tag)
        text = text.decode("utf-8")
        _type = text[:9].split("|")[0].strip()
        content = text[9:]
        return mappings[_type](content)

    @staticmethod
    def __ensure_ignore_fields(ignore_fields: Optional[IgnoreFields]):
        if ignore_fields is not None:
            return ignore_fields

        return IgnoreFields()

    def __preprocess_fields(
        self, data: Union[Dict, Saveable], ignore_fields: IgnoreFields
    ):
        if isinstance(data, Saveable):
            data = data.as_dict()

        if not isinstance(data, dict):
            raise ValueError(f"Expected dict, got {data.__class__.__name__}")

        return self._encrypt_data(data, ignore_fields=ignore_fields)

    async def _attempt_convert(
        self, data: Union[Dict, List[Dict]]
    ) -> Union[List[Union[Dict[str, Any], Type[T]]], Union[Dict[str, Any], Type[T]]]:
        if not data:
            return data

        if not self.converter:
            if isinstance(data, list):
                out = []
                for itr in data:
                    out.append(self._decrypt_data(itr))
                return out

            return self._decrypt_data(data)

        if not isinstance(data, list):
            return self.converter(**self._decrypt_data(data))

        new_data = []
        for d in data:
            new_data.append(self.converter(**self._decrypt_data(d)))

        return new_data

    async def insert(
        self,
        data: Union[Dict[str, Any], Saveable],
        *,
        ignore_fields: Optional[IgnoreFields] = None,
    ) -> None:
        """Insert the provided data into the document.

        Parameters
        ----------
        data: Union[Dict[str, Any], Saveable]
            The data to insert
        ignore_fields: Optional[IgnoreFields]
            Any fields to ignore during the hashing / encryption step.

            Useful if your passing this method an already hashed value
            and you don't want to hash the hash.

        .. code-block:: python
            :linenos:

            # If you don't provide an _id,
            # Mongo will generate one for you automatically
            await Document.insert({"_id": 1, "data": "hello world"})
        """
        ignore_fields = self.__ensure_ignore_fields(ignore_fields=ignore_fields)
        data = self.__preprocess_fields(data, ignore_fields=ignore_fields)
        await super().insert(data)

    async def update(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        update_data: Union[Dict[str, Any], Saveable],
        option: str = "set",
        *args: Any,
        ignore_fields: Optional[IgnoreFields] = None,
        **kwargs: Any,
    ) -> None:
        """Performs an UPDATE operation.

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], Buildable, Filterable]
            The data to filter on
        update_data: Union[Dict[str, Any], Saveable]
            The data to upsert
        option: str
            The optional option to pass to mongo,
            default is set

            https://www.mongodb.com/docs/manual/reference/operator/update/
        ignore_fields: Optional[IgnoreFields]
            Any fields to ignore during the hashing / encryption step.

            Useful if your passing this method an already hashed value
            and you don't want to hash the hash.


        .. code-block:: python
            :linenos:

            # Update the document with an `_id` of 1
            # So that it now equals the second argument
            await Document.upsert({"_id": 1}, {"_id": 1, "data": "new data"})
        """
        ignore_fields = self.__ensure_ignore_fields(ignore_fields=ignore_fields)
        update_data = self.__preprocess_fields(update_data, ignore_fields=ignore_fields)
        await super().update(filter_dict, update_data)

    async def upsert(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        update_data: Union[Dict[str, Any], Saveable],
        option: str = "set",
        *args: Any,
        ignore_fields: Optional[IgnoreFields] = None,
        **kwargs: Any,
    ) -> None:
        """Performs an UPSERT operation.

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], Buildable, Filterable]
            The data to filter on
        update_data: Union[Dict[str, Any], Saveable]
            The data to upsert
        option: str
            Update operator.

            https://www.mongodb.com/docs/manual/reference/operator/update/
        ignore_fields: Optional[IgnoreFields]
            Any fields to ignore during the hashing / encryption step.

            Useful if your passing this method an already hashed value
            and you don't want to hash the hash.


        .. code-block:: python
            :linenos:

            # Update the document with an `_id` of `1`
            # So that it now equals the second argument
            # NOTE: If a document with an `_id` of `1`
            # does not exist, then this method will
            # insert the data instead.
            await Document.update({"_id": 1}, {"_id": 1, "data": "new data"})
        """
        ignore_fields = self.__ensure_ignore_fields(ignore_fields=ignore_fields)
        update_data = self.__preprocess_fields(update_data, ignore_fields=ignore_fields)
        await super().upsert(filter_dict, update_data)

    async def increment(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        field: str,
        amount: Union[int, float],
    ) -> None:
        """Increment the provided field.

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], Buildable, Filterable]
            The 'thing' we want to increment
        field: str
            The key for the field to increment
        amount: Union[int, float]
            How much to increment (or decrement) by

        Notes
        -----
        This seamlessly handles incrementing encrypted fields.

        .. code-block:: python
            :linenos:

            # Assuming a data structure of
            # {"_id": 1, "counter": 4}
            await Document.increment({"_id": 1}, "counter", 1)

            # Now looks like
            # {"_id": 1, "counter": 5}

        Raises
        ------
        ValueError
            Nested field updates on encrypted fields is not supported.
        ValueError
            Item to increment didn't exist with this filter.

        Notes
        -----
        You can also use negative numbers to
        decrease the count of a field.
        """
        if field not in self._encrypted_fields:
            return await super().increment(filter_dict, field, amount)

        if "." in field:
            raise ValueError(
                "Nested field updates on encrypted fields is not supported."
            )

        data: Dict = await self.find(  # noqa
            filter_dict, projections=Projection(Show(field)), try_convert=False
        )
        if not data:
            raise ValueError("Item to increment didn't exist with this filter.")

        data[field] += amount
        await self.update(filter_dict, data)

    async def change_field_to(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        field: str,
        new_value: Any,
    ) -> None:
        """Modify a single field and change the value.

        Parameters
        ----------
        filter_dict: Union[Dict[Any, Any], Buildable, Filterable]
            A dictionary to use as a filter or
            :py:class:`AQ` object.
        field: str
            The key for the field to increment
        new_value: Any
            What the field should get changed to


        .. code-block:: python
            :linenos:

            # Assuming a data structure of
            # {"_id": 1, "prefix": "!"}
            await Document.change_field_to({"_id": 1}, "prefix", "?")

            # This will now look like
            # {"_id": 1, "prefix": "?"}
        """
        if field in self._encrypted_fields:
            new_value = self._aes_encrypt_field(new_value)

        await super().change_field_to(filter_dict, field, new_value)

    async def bulk_insert(
        self,
        data: List[Dict],
        ignore_fields: Optional[IgnoreFields] = None,
    ) -> None:
        """
        Given a List of Dictionaries, bulk insert all
        the given dictionaries in a single call.

        Notes
        -----
        Supports encrypted and hashed fields.

        Parameters
        ----------
        data: List[Dict]
            The data to bulk insert
        ignore_fields: Optional[IgnoreFields]
            Any fields to ignore during the hashing / encryption step.

            Useful if your passing this method an already hashed value
            and you don't want to hash the hash.


        .. code-block:: python
            :linenos:

            # Insert 25 documents
            await Document.bulk_insert(
                {"_id": i}
                for i in range(25)
            )
        """
        ignore_fields = self.__ensure_ignore_fields(ignore_fields=ignore_fields)
        self._ensure_list_of_dicts(data)
        encrypted_data = []
        for d in data:
            encrypted_data.append(self._encrypt_data(d, ignore_fields=ignore_fields))

        await self._document.insert_many(encrypted_data)

    if TYPE_CHECKING:
        # I don't like this but Pycharm doesn't
        # properly support methods from parents
        async def find(
            self,
            filter_dict: Union[Dict[str, Any], Buildable, Filterable],
            projections: Optional[Union[Dict[str, Any], Projection]] = None,
            *,
            try_convert: bool = True,
        ) -> Optional[Union[Dict[str, Any], Type[T]]]:
            ...

        async def find_many(
            self,
            filter_dict: Union[Dict[str, Any], Buildable, Filterable],
            projections: Optional[Union[Dict[str, Any], Projection]] = None,
            *,
            try_convert: bool = True,
        ) -> List[Union[Dict[str, Any], Type[T]]]:
            ...

        async def delete(
            self,
            filter_dict: Union[Dict, Buildable, Filterable],
        ) -> Optional[DeleteResult]:
            ...

        async def get_all(
            self,
            filter_dict: Optional[Union[Dict[str, Any], Buildable, Filterable]] = None,
            projections: Optional[Union[Dict[str, Any], Projection]] = None,
            *args: Any,
            try_convert: bool = True,
            **kwargs: Any,
        ) -> List[Optional[Union[Dict[str, Any], Type[T]]]]:
            ...

        async def count(
            self, filter_dict: Union[Dict[Any, Any], Buildable, Filterable]
        ) -> int:
            ...
