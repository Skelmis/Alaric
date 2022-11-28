from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Dict, List, Tuple, Union, Literal

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorCursor

from alaric.abc import Buildable, Filterable
from alaric.meta import All
from alaric.projections import Projection

if TYPE_CHECKING:
    from alaric import Document


class Cursor:
    def __init__(self, collection: AsyncIOMotorCollection):
        self._collection: AsyncIOMotorCollection = collection
        self._filter: Dict[str, Any] = {}
        self._projections: Optional[Dict[str, Any]] = None
        self._limit: int = 0  # Amount of items to return
        self._sort: Optional[List[Tuple[str, Any]], Tuple[str, Any]] = None
        self._cursor: Optional[AsyncIOMotorCursor] = None

    @classmethod
    def from_document(cls, document: Document) -> Cursor:
        return cls(document.raw_collection)

    @staticmethod
    def __ensure_built(data: Union[Dict, Buildable, Filterable]) -> Dict:
        if isinstance(data, Filterable):
            return data.as_filter()

        elif isinstance(data, Buildable):
            return data.build()

        return data

    def _ensure_modifiable(self):
        if self._cursor is not None:
            raise ValueError(
                "Cursor is already in use, create a copy and modify that instance."
            )

    def copy(self) -> Cursor:
        """Returns a modifiable version of this cursor.

        Returns
        -------
        Cursor
            A new cursor instance
        """
        cursor: Cursor = Cursor(self._collection)
        cursor._sort = self._sort
        cursor._limit = self._limit
        cursor._filter = self._filter
        cursor._projections = self._projections
        return cursor

    def _build_cursor(self):
        self._ensure_modifiable()
        if self._projections:
            motor_cursor = self._collection.find(self._filter, self._projections)
        else:
            motor_cursor = self._collection.find(self._filter)

        if self._sort:
            motor_cursor = motor_cursor.sort(self._sort)
        if self._limit:
            motor_cursor = motor_cursor.limit(self._limit)

        self._cursor = motor_cursor

    def set_filter(
        self,
        filter_data: Union[
            Dict[str, Any],
            Buildable,
            Filterable,
        ] = All(),
    ) -> Cursor:
        """Set the filter for the cursor query.

        Parameters
        ----------
        filter_data: Union[Dict[str, Any], Buildable, Filterable]
            A dictionary to use as a filter or
            :py:class:`AQ` object.

        Returns
        -------
        Cursor
            This cursor instance for method chaining.
        """
        self._ensure_modifiable()
        self._filter = self.__ensure_built(filter_data)
        return self

    def set_projections(
        self,
        projections: Optional[Union[Dict[str, Literal[0, 1]], Projection]] = None,
    ) -> Cursor:
        """Define what data should be returned for each document in the result

        Parameters
        ----------
        projections: Optional[Union[Dict[str, Literal[0, 1]], Projection]]
            Specify the data you want returned from matching queries.

        Returns
        -------
        Cursor
            This cursor instance for method chaining.
        """
        self._ensure_modifiable()
        self._projections = self.__ensure_built(projections)
        return self

    def set_limit(self, limit: int = 0) -> Cursor:
        """Set a limit for how many documents should
        be returned in the query.

        Use ``0`` to indicate no limit.

        Parameters
        ----------
        limit: int
            How many documents should be returned.

            Defaults to no limit.

        Returns
        -------
        Cursor
            This cursor instance for method chaining.

        Raises
        ------
        ValueError
            You specified a negative number.
        """
        self._ensure_modifiable()
        if not isinstance(limit, int) or limit < 0:
            raise ValueError("Positive numbers only")

        self._limit = limit
        return self

    def set_sort(
        self, order: Optional[List[Tuple[str, Any]], Tuple[str, Any]] = None
    ) -> Cursor:
        """Set the sort order for returned results

        Parameters
        ----------
        order: Optional[List[Tuple[str, Any]], Tuple[str, Any]]
            The order to sort by

        Returns
        -------
        Cursor
            This cursor instance for method chaining

        Raises
        ------
        ValueError
            The passed value was not a list or tuple

        .. code-block:: python
            :linenos:

            import alaric

            # Lets sort by the count field
            Cursor.set_sort(("count", alaric.Ascending))

            ...
            # Lets sort first by the count field,
            # then also by the backup_count field
            Cursor.set_sort([("count", alaric.Ascending), ("backup_count", alaric.Descending)])
        """
        self._ensure_modifiable()
        # TODO: Make a sort object with fields to more easily support advanced sorting?
        if not isinstance(order, list) and order is not None:
            if isinstance(order, tuple):
                order = [order]
            else:
                raise ValueError("order must be either a tuple, or list of tuples")

        self._sort = order
        return self

    async def execute(self) -> List:
        """Execute this cursor and return the result."""
        self._build_cursor()
        return await self._cursor.to_list(None)

    def __aiter__(self):
        self._build_cursor()
        return self

    async def __anext__(self):
        async for item in self._cursor:
            return item

        raise StopAsyncIteration
