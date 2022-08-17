from typing import List, Dict, Optional, Union, Any, TypeVar, Type

from pymongo.results import DeleteResult
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from alaric.abc import Buildable, Filterable, Saveable
from alaric.projections import Projection

T = TypeVar("T")
"""A typevar representing the type of a given converter class"""


class Document:
    _version = 11

    def __init__(
        self,
        database: AsyncIOMotorDatabase,
        document_name: str,
        converter: Optional[Type[T]] = None,
    ):
        """
        Parameters
        ----------
        database: AsyncIOMotorDatabase
            The database we are connected to
        document_name: str
            What this _document should be called
        converter: Optional[Type[:py:class:`~alaric.document.T`]]
            An optional class to try
            to convert all data-types which
            return either Dict or List into


        .. code-block:: python
            :linenos:

            from motor.motor_asyncio import AsyncIOMotorClient

            client = AsyncIOMotorClient(connection_url)
            database = client["my_database"]
            config_document = Document(database, "config")
        """
        self._document_name: str = document_name
        self._database: AsyncIOMotorDatabase = database
        self._document: AsyncIOMotorCollection = database[document_name]  # type: ignore

        self.converter: Type[T] = converter

    def __repr__(self):
        return f"<Document(document_name={self.collection_name})>"

    async def find(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        projections: Optional[Union[Dict[str, Any], Projection]] = None,
        *,
        try_convert: bool = True,
    ) -> Optional[Union[Dict[str, Any], Type[T]]]:
        """Find and return one item.

        Parameters
        ----------
        filter_dict: Union[Dict, Buildable, Filterable]
            A dictionary to use as a filter or
            :py:class:`AQ` object.
        projections: Optional[Union[Dict[str, Any], Projection]]
            Specify the data you want
            returned from matching queries.
        try_convert: bool
            Whether to attempt to
            run convertors on returned data.

            Defaults to True

        Returns
        -------
        Optional[Union[Dict[str, Any], Type[:py:class:`~alaric.document.T`]]]
            The result of the query


        .. code-block:: python
            :linenos:

            # Find the document where the `_id` field is equal to `my_id`
            data: dict = await Document.find({"_id": "my_id"})
        """
        filter_dict = self.__ensure_built(filter_dict)
        projections = projections or {}
        projections = self.__ensure_built(projections)

        if projections:
            data = await self._document.find_one(filter_dict, projections)
        else:
            data = await self._document.find_one(filter_dict)

        if try_convert:
            return await self._attempt_convert(data)
        return data

    async def find_many(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        projections: Optional[Union[Dict[str, Any], Projection]] = None,
        *,
        try_convert: bool = True,
    ) -> List[Union[Dict[str, Any], Type[T]]]:
        """
        Find and return all items
        matching the given filter.

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], Buildable, Filterable]
            A dictionary to use as a filter or
            :py:class:`AQ` object.
        projections: Optional[Union[Dict[str, Any], Projection]]
            Specify the data you want
            returned from matching queries.
        try_convert: bool
            Whether to attempt to
            run convertors on returned data.

            Defaults to True

        Returns
        -------
        List[Union[Dict[str, Any], Type[:py:class:`~alaric.document.T`]]]
            The result of the query


        .. code-block:: python
            :linenos:

            # Find all documents where the key `my_field` is `true`
            data: list[dict] = await Document.find_many({"my_field": True})
        """
        filter_dict = self.__ensure_built(filter_dict)
        projections = projections or {}
        projections = self.__ensure_built(projections)

        if projections:
            data = await self._document.find(filter_dict, projections).to_list(None)  # type: ignore
        else:
            data = await self._document.find(filter_dict).to_list(None)  # type: ignore

        if try_convert:
            return await self._attempt_convert(data)
        return data

    async def delete(
        self,
        filter_dict: Union[Dict, Buildable, Filterable],
    ) -> Optional[DeleteResult]:
        """
        Delete an item from the Document
        if an item with the provided filter exists.

        Parameters
        ----------
        filter_dict: Union[Dict, Buildable, Filterable]
            A dictionary to use as a filter or
            :py:class:`AQ` object.

        Returns
        -------
        Optional[DeleteResult]
            The result of deletion if it occurred.


        .. code-block:: python
            :linenos:

            # Delete items with a `prefix` of `!`
            await Document.delete({"prefix": "!"})
        """
        filter_dict = self.__ensure_built(filter_dict)
        result: DeleteResult = await self._document.delete_many(filter_dict)
        result: Optional[DeleteResult] = result if result.deleted_count != 0 else None
        return result

    async def delete_all(self) -> None:
        """Delete all data associated with this document.

        Notes
        -----
        This will attempt to complete the operation
        in a single call, however, if that fails it
        will fall back to manually deleting items one by one.

        Warnings
        --------
        There is no going back if you call this accidentally.

        This also currently doesn't appear to work.
        """
        try:
            await self._document.drop()
        except:  # noqa
            for entry in await self.get_all(try_convert=False):
                await self.delete(entry)

    async def get_all(
        self,
        filter_dict: Optional[Union[Dict[str, Any], Buildable, Filterable]] = None,
        projections: Optional[Union[Dict[str, Any], Projection]] = None,
        *args: Any,
        try_convert: bool = True,
        **kwargs: Any,
    ) -> List[Optional[Union[Dict[str, Any], Type[T]]]]:
        """
        Fetches and returns all items
        which match the given filter.

        Parameters
        ----------
        filter_dict: Optional[Union[Dict[str, Any], Buildable, Filterable]]
            A dictionary to use as a filter or
            :py:class:`AQ` object.
        projections: Optional[Union[Dict[str, Any], Projection]]
            Specify the data you want
            returned from matching queries.
        try_convert: bool
            Whether to attempt to
            run convertors on returned data.

            Defaults to True

        Returns
        -------
        List[Optional[Union[Dict[str, Any], Type[:py:class:`~alaric.document.T`]]]]
            The items matching the filter


        .. code-block:: python
            :linenos:

            data: list[dict] = await Document.get_all()
        """
        filter_dict = filter_dict or {}
        filter_dict = self.__ensure_built(filter_dict)

        projections = projections or {}
        projections = self.__ensure_built(projections)

        if projections:
            data = await self._document.find(
                filter_dict, projections, *args, **kwargs
            ).to_list(
                None  # type: ignore
            )
        else:
            data = await self._document.find(filter_dict, *args, **kwargs).to_list(None)  # type: ignore

        if try_convert:
            return await self._attempt_convert(data)
        return data

    async def insert(self, data: Union[Dict[str, Any], Saveable]) -> None:
        """Insert the provided data into the document.

        Parameters
        ----------
        data: Union[Dict[str, Any], Saveable]
            The data to insert


        .. code-block:: python
            :linenos:

            # If you don't provide an _id,
            # Mongo will generate one for you automatically
            await Document.insert({"_id": 1, "data": "hello world"})
        """
        data = self.__ensure_insertable(data)
        await self._document.insert_one(data)

    async def update(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        update_data: Union[Dict[str, Any], Saveable],
        option: str = "set",
        *args: Any,
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


        .. code-block:: python
            :linenos:

            # Update the document with an `_id` of 1
            # So that it now equals the second argument
            await Document.upsert({"_id": 1}, {"_id": 1, "data": "new data"})
        """
        filter_dict = self.__ensure_built(filter_dict)
        update_data = self.__ensure_insertable(update_data)

        await self._document.update_one(
            filter_dict, {f"${option}": update_data}, *args, **kwargs
        )

    async def upsert(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        update_data: Union[Dict[str, Any], Saveable],
        option: str = "set",
        *args: Any,
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


        .. code-block:: python
            :linenos:

            # Update the document with an `_id` of `1`
            # So that it now equals the second argument
            # NOTE: If a document with an `_id` of `1`
            # does not exist, then this method will
            # insert the data instead.
            await Document.update({"_id": 1}, {"_id": 1, "data": "new data"})
        """
        filter_dict = self.__ensure_built(filter_dict)
        update_data = self.__ensure_insertable(update_data)
        await self.update(
            filter_dict, update_data, option, upsert=True, *args, **kwargs
        )

    async def unset(
        self, filter_dict: Union[Dict[str, Any], Buildable, Filterable], field: Any
    ) -> None:
        """Delete a given field on a collection

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], Buildable, Filterable]
            The fields to match on (Think _id)
        field: Any
            The field to remove


        .. code-block:: python
            :linenos:

            # Assuming we have a document that looks like
            # {"_id": 1, "field_one": True, "field_two": False}
            await Document.unset({"_id": 1}, "field_two")

            # This data will now look like the following
            # {"_id": 1, "field_one": True}
        """
        filter_dict = self.__ensure_built(filter_dict)
        await self._document.update_one(filter_dict, {"$unset": {field: True}})

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


        .. code-block:: python
            :linenos:

            # Assuming a data structure of
            # {"_id": 1, "counter": 4}
            await Document.increment({"_id": 1}, "counter", 1)

            # Now looks like
            # {"_id": 1, "counter": 5}

        Notes
        -----
        You can also use negative numbers to
        decrease the count of a field.
        """
        filter_dict = self.__ensure_built(filter_dict)
        await self._document.update_one(filter_dict, {"$inc": {field: amount}})

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
        filter_dict = self.__ensure_built(filter_dict)
        await self._document.update_one(filter_dict, {"$set": {field: new_value}})

    async def count(
        self, filter_dict: Union[Dict[Any, Any], Buildable, Filterable]
    ) -> int:
        """Return a count of how many items match the filter.

        Parameters
        ----------
        filter_dict:  Union[Dict[Any, Any], Buildable, Filterable]
            The count filer.

        Returns
        -------
        int
            How many items matched the filter.


        .. code-block:: python
            :linenos:

            # How many items have the `enabled` field set to True
            count: int = await Document.count({"enabled": True})
        """
        filter_dict = self.__ensure_built(filter_dict)
        return await self._document.count_documents(filter_dict)

    async def bulk_insert(self, data: List[Dict]) -> None:
        """
        Given a List of Dictionaries, bulk insert all
        the given dictionaries in a single call.

        Parameters
        ----------
        data: List[Dict]
            The data to bulk insert


        .. code-block:: python
            :linenos:

            # Insert 25 documents
            await Document.bulk_insert(
                {"_id": i}
                for i in range(25)
            )
        """
        self.__ensure_list_of_dicts(data)
        await self._document.insert_many(data)

    # <-- Private methods -->
    @staticmethod
    def __ensure_list_of_dicts(data: List[Dict]):
        assert isinstance(data, list)
        assert all(isinstance(entry, dict) for entry in data)

    @staticmethod
    def __ensure_insertable(data: Union[Dict, Saveable]) -> Dict:
        if isinstance(data, Saveable):
            return data.as_dict()

        if not isinstance(data, Dict):
            raise ValueError(f"Expected dict, got {data.__class__.__name__}")

        return data

    @staticmethod
    def __ensure_built(data: Union[Dict, Buildable, Filterable]) -> Dict:
        if isinstance(data, Filterable):
            return data.as_filter()

        elif isinstance(data, Buildable):
            return data.build()

        return data

    async def _attempt_convert(
        self, data: Union[Dict, List[Dict]]
    ) -> Union[List[Union[Dict[str, Any], Type[T]]], Union[Dict[str, Any], Type[T]]]:
        # This exists purely so we don't lose intelli-sense
        # as decorators remove intelli-sense
        if not data or not self.converter:
            return data

        if not isinstance(data, list):
            return self.converter(**data)

        new_data = []
        for d in data:
            new_data.append(self.converter(**d))

        return new_data

    # <-- Some basic internals -->
    @property
    def collection_name(self) -> str:
        """The connected collections name."""
        return self._document_name

    @property
    def document_name(self) -> str:
        """Same as :py:meth:`~alaric.Document.collection_name`"""
        return self._document_name

    @property
    def raw_database(self) -> AsyncIOMotorDatabase:
        """Access to the database instance."""
        return self._database

    @property
    def raw_collection(self) -> AsyncIOMotorCollection:
        """The connection collection instance."""
        return self._document
