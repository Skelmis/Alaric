from __future__ import annotations

import io
import logging
from datetime import timedelta
from typing import (
    TYPE_CHECKING,
    List,
    Union,
    Dict,
    Any,
    Optional,
    TypeVar,
    cast,
    Generic,
)

import orjson

from alaric.abc import Buildable, Filterable, Saveable

if TYPE_CHECKING:
    from redis.asyncio.client import Redis
    from alaric import Document


log = logging.getLogger(__name__)
C = TypeVar("C")
"""A typevar representing the type of a given converter class"""


class CachedDocument(Generic[C]):
    """This document implements a cache in front of MongoDB for read heavy work flows.

    Read process:

    .. code-block:: text

        result = attempt to hit redis
        if result is None:
            result = fetch from database
            populate redis cache

    Write process:

    .. code-block:: text

        Push changes back to database
        update redis cache

    Notes
    -----
    This document works off the assumption that a documents ``_id`` remains
    consistent through the lifetime of the entry.

    This document will also leave hanging redis entries when lookups
    outside the _id are modified during the lifetime of the object.
    This is mitigated by enforcing a TTL of all redis entries.
    """

    def __init__(
        self,
        *,
        document: Document,
        redis_client: Redis,
        extra_lookups: List[List[str]] = None,
        cache_ttl: timedelta = timedelta(hours=1),
    ):
        """

        Parameters
        ----------
        document: alaric.Document
            The underlying DB document
        redis_client: redis.asyncio.client.Redis
            The Redis instance to use
        extra_lookups: List[List[str]]
            Extra lookups to build. For example:

            .. code-block:: python

                class Test:
                    def __init__(self, _id, data):
                        self.data = data
                        self._id = _id

                ...

                extra_lookups = [["data"]]

            Would let you use ``get`` with either the
            ``_id`` or ``data`` parameter of ``Test``

        cache_ttl: timedelta
            How long keys should exist in Redis.

            This is a requirement as this class will
            leave hanging keys in Redis when certain values change.
        """
        self.document: Document = document
        self._redis_client: Redis = redis_client
        self._cache_ttl: timedelta = cache_ttl
        self._extra_lookups: List[List[str]] = []
        if extra_lookups is not None:
            # keys are sorted so that we can consistently
            # do redis lookups without the need for more than
            # a straight string key lookup
            for lookup in extra_lookups:
                self._extra_lookups.append(sorted(lookup))

    async def get(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        *,
        try_convert: bool = True,
    ) -> Optional[Union[Dict[str, Any], C]]:
        """Fetch a document.

        Attempts to fetch from Redis and then falls back to DB

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], Buildable, Filterable]
        try_convert: bool
            See :py:class:`alaric.Document`

        Returns
        -------
        Optional[Union[Dict[str, Any], C]]
            The data fetched from either Redis or your DB

        Notes
        -----
        Due to how items are stored internally,
        filter_dict must eval to a literal str: str
        pairing otherwise this will fall back to the DB

        """
        filter_dict: Dict[str, str] = self.document._ensure_built(filter_dict)
        lookup_key = original_key = self._build_redis_lookup_key(filter_dict)

        # If not a straight _id lookup, resolve the chain
        # back to the raw data itself. We also assume that
        # any lookup key which does not start with _id
        # requires resolving back the source
        if not lookup_key.startswith("_id:"):
            new_lookup_key = await self._redis_client.get(lookup_key)
            if new_lookup_key is not None:
                # If It's None, just do the check as is and
                # call it a day
                lookup_key = new_lookup_key

        result = await self._redis_client.get(lookup_key)
        if result is None:
            result = await self.document.find(filter_dict, try_convert=False)
            if result is not None:
                result = cast(Dict[str, Any], result)
                await self._update_redis_cache(result)

            log.debug("Cache miss for %s", original_key)
        else:
            result = orjson.loads(result)
            log.debug("Cache hit for %s", original_key)

        if try_convert:
            return await self.document._attempt_convert(result)
        return result

    async def set(
        self,
        filter_dict: Union[Dict[str, Any], Buildable, Filterable],
        update_data: Union[Dict[str, Any], Saveable],
    ) -> None:
        """Write to Redis and the DB.

        Notes
        -----
        This performs an UPSERT operation
        on the database.

        This also requires ``_id`` to be set on update_data
        in order to cache this to Redis

        Parameters
        ----------
        filter_dict: Union[Dict[str, Any], Buildable, Filterable]
        update_data: Union[Dict[str, Any], Saveable]
        """
        filter_dict = self.document._ensure_built(filter_dict)
        update_data = self.document._ensure_insertable(update_data)
        if "_id" not in update_data:
            log.warning("Failed to cache data as _id was missing: %s", update_data)
        else:
            await self._update_redis_cache(update_data)

        await self.document.upsert(filter_dict, update_data)

    async def _update_redis_cache(self, data: Dict[str, Any]):
        """Updates the redis cache data entries"""
        assert "_id" in data
        data_id = data["_id"]
        data_id_key = f"_id:{data_id}|"
        data_str = orjson.dumps(data)
        await self._redis_client.setex(data_id_key, self._cache_ttl, data_str)

        for lookup_entry in self._extra_lookups:
            key = io.StringIO()
            for item in lookup_entry:
                key.write(f"{item}:{data[item]}|")

            await self._redis_client.setex(key.getvalue(), self._cache_ttl, data_id_key)

    @staticmethod
    def _build_redis_lookup_key(filter_dict: Dict[str, str]) -> str:
        """Given a dict, build the redis lookup key"""
        # Redis key format
        # field_name:field_value|
        # The key should contain a trailing pipe
        result = io.StringIO()
        for key in sorted(filter_dict.keys()):
            result.write(f"{key}:{filter_dict[key]}|")

        return result.getvalue()
