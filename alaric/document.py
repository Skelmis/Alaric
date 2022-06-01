import functools
from typing import List, Dict, Optional, Union, Any, TypeVar, Type

from pymongo.results import DeleteResult
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from alaric.abc import BuildAble

T = TypeVar("T")


class Document:
    _version = 10

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
        converter: Optional[Type[T]]
            An optional class to try
            to convert all data-types which
            return either Dict or List into
        """
        self._document_name: str = document_name
        self._database: AsyncIOMotorDatabase = database
        self._document: AsyncIOMotorCollection = database[document_name]

        self.converter: Type[T] = converter

    def __repr__(self):
        return f"<Document(document_name={self.collection_name})>"

    async def find(
        self, filter_dict: Union[Dict[str, Any], BuildAble]
    ) -> Optional[Union[Dict[str, Any], Type[T]]]:
        """Find and return one item.

        Parameters
        ----------
        filter_dict: Union[Dict, BuildAble]
            A dictionary to use as a filter or
            :py:class:`AQ` object.

        Returns
        -------
        Optional[Union[Dict[str, Any], Type[T]]]
            The result of the query
        """
        filter_dict = self.__ensure_built(filter_dict)
        self.__ensure_dict(filter_dict)
        data = await self._document.find_one(filter_dict)
        return await self.attempt_convert(data)

    async def find_many(
        self, filter_dict: Union[Dict[str, Any], BuildAble]
    ) -> List[Union[Dict[str, Any], Type[T]]]:
        """
        Find and return all items
        matching the given filter.

        Parameters
        ----------
        filter_dict: Dict[str, Any]
            A dictionary to use as a filter or
            :py:class:`AQ` object.

        Returns
        -------
        List[Union[Dict[str, Any], Type[T]]]
            The result of the query
        """
        filter_dict = self.__ensure_built(filter_dict)
        self.__ensure_dict(filter_dict)
        data = await self._document.find(filter_dict).to_list(None)
        return await self.attempt_convert(data)

    async def delete(
        self, filter_dict: Union[Dict, BuildAble]
    ) -> Optional[DeleteResult]:
        """
        Delete an item from the Document
        if an item with the provided filter exists.

        Parameters
        ----------
        filter_dict: Union[Dict, BuildAble]
            A dictionary to use as a filter or
            :py:class:`AQ` object.

        Returns
        -------
        Optional[DeleteResult]
            The result of deletion if it occurred.
        """
        filter_dict = self.__ensure_built(filter_dict)
        self.__ensure_dict(filter_dict)
        result: DeleteResult = await self._document.delete_many(filter_dict)
        result: Optional[DeleteResult] = result if result.deleted_count != 0 else None
        return result

    async def get_all(
        self,
        filter_dict: Optional[Union[Dict[str, Any], BuildAble]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> List[Optional[Union[Dict[str, Any], Type[T]]]]:
        """
        Fetches and returns all items
        which match the given filter.

        Example usages

        .. code-block:: python
            results = await document.get_all()

            ...

            # Get all documents with a given field
            results = await document.get_all(AQ(EXISTS("field")))

        Parameters
        ----------
        filter_dict: Optional[Dict[str, Any]]
            A dictionary to use as a filter or
            :py:class:`AQ` object.

        Returns
        -------
        List[Optional[Union[Dict[str, Any], Type[T]]]]
            The items matching the filter
        """
        filter_dict = filter_dict or {}
        filter_dict = self.__ensure_built(filter_dict)

        data = await self._document.find(filter_dict, *args, **kwargs).to_list(None)
        return await self.attempt_convert(data)

    async def insert(self, data: Dict[str, Any]) -> None:
        """Insert the provided data into the document.

        Parameters
        ----------
        data: Dict[str, Any]
            The data to insert
        """
        self.__ensure_dict(data)
        await self._document.insert_one(data)

    async def update(
        self,
        filter_dict: Union[Dict[str, Any], BuildAble],
        update_data: Dict[str, Any],
        option: str = "set",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Performs an UPDATE operation.

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], BuildAble]
            The data to filter on
        update_data: Dict[str, Any]
            The data to upsert
        option: str
            The optional option to pass to mongo,
            default is set
            https://www.mongodb.com/docs/manual/reference/operator/update/
        """
        filter_dict = self.__ensure_built(filter_dict)
        self.__ensure_dict(filter_dict)
        self.__ensure_dict(update_data)

        await self._document.update_one(
            filter_dict, {f"${option}": update_data}, *args, **kwargs
        )

    async def upsert(
        self,
        filter_dict: Union[Dict[str, Any], BuildAble],
        update_data: Dict[str, Any],
        option: str = "set",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Performs an UPSERT operation.

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], BuildAble]
            The data to filter on
        update_data: Dict[str, Any]
            The data to upsert
        option: str
            Update operator.
            https://www.mongodb.com/docs/manual/reference/operator/update/
        """
        filter_dict = self.__ensure_built(filter_dict)
        self.__ensure_dict(filter_dict)
        self.__ensure_dict(update_data)
        await self.update(
            filter_dict, update_data, option, upsert=True, *args, **kwargs
        )

    async def unset(
        self, filter_dict: Union[Dict[str, Any], BuildAble], field: Any
    ) -> None:
        """Delete a given field on a collection

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], BuildAble]
            The fields to match on (Think _id)
        field: Any
            The field to remove
        """
        filter_dict = self.__ensure_built(filter_dict)
        self.__ensure_dict(filter_dict)
        await self._document.update_one(filter_dict, {"$unset": {field: True}})

    async def increment(
        self,
        filter_dict: Union[Dict[str, Any], BuildAble],
        field: str,
        amount: Union[int, float],
    ) -> None:
        """Increment the provided field.

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], BuildAble]
            The 'thing' we want to increment
        field: str
            The key for the field to increment
        amount: Union[int, float]
            How much to increment (or decrement) by
        """
        filter_dict = self.__ensure_built(filter_dict)
        self.__ensure_dict(filter_dict)
        await self._document.update_one(filter_dict, {"$inc": {field: amount}})

    async def change_field_to(
        self,
        filter_dict: Union[Dict[str, Any], BuildAble],
        field: str,
        new_value: Any,
    ) -> None:
        """Modify a single field and change the value.

        Parameters
        ----------
        filter_dict: Union[Dict[Any, Any], BuildAble]
            A dictionary to use as a filter or
            :py:class:`AQ` object.
        field: str
            The key for the field to increment
        new_value: Any
            What the field should get changed to
        """
        filter_dict = self.__ensure_built(filter_dict)
        self.__ensure_dict(filter_dict)
        await self._document.update_one(filter_dict, {"$set": {field: new_value}})

    async def count(self, filter_dict: Union[Dict[Any, Any], BuildAble]) -> int:
        """Return a count of how many items match the filter.

        Parameters
        ----------
        filter_dict:  Union[Dict[Any, Any], BuildAble]
            The count filer.

        Returns
        -------
        int
            How many items matched the filter.
        """
        filter_dict = self.__ensure_built(filter_dict)
        self.__ensure_dict(filter_dict)
        return await self._document.count_documents(filter_dict)

    async def bulk_insert(self, data: List[Dict]) -> None:
        """
        Given a List of Dictionaries, bulk insert all
        the given dictionaries in a single call.

        Parameters
        ----------
        data: List[Dict]
            The data to bulk insert
        """
        self.__ensure_list_of_dicts(data)
        await self._document.insert_many(data)

    # <-- Private methods -->
    @staticmethod
    def __ensure_list_of_dicts(data: List[Dict]):
        assert isinstance(data, list)
        assert all(isinstance(entry, dict) for entry in data)

    @staticmethod
    def __ensure_dict(data: Dict[str, Any]) -> None:
        assert isinstance(data, dict)

    @staticmethod
    def __ensure_built(data: Union[Dict, BuildAble]) -> Dict:
        if isinstance(data, BuildAble):
            return data.build()

        return data

    async def attempt_convert(
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
        return self._document_name

    @property
    def raw_database(self) -> AsyncIOMotorDatabase:
        """Access to the database instance."""
        return self._database

    @property
    def raw_collection(self) -> AsyncIOMotorCollection:
        """The connection collection instance."""
        return self._document
