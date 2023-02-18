from __future__ import annotations

import hashlib
from typing import Union, Dict

from alaric.abc import ComparisonT
from alaric.types import ObjectId


class HashedQueryField:
    """Use this to query against hashed fields.

    This class exposes an alias `HQF` for shorter usage.

    .. code-block:: python

        from alaric import AQ
        from alaric.comparison import EQ
        from alaric.encryption import HQF

        query = AQ(HQF(EQ("_id", 1)))
    """

    def __init__(self, entry: ComparisonT):
        self._entry: ComparisonT = entry

    def build(
        self,
    ) -> Dict[str, Dict[str, Union[int, str, float, bytes, dict, ObjectId]]]:
        """Return this instance as a usable Mongo filter."""
        initial = self._entry.build()
        out = {}
        for k, v in initial.items():
            d = {}
            for nested_k, nested_v in v.items():
                d[nested_k] = self._hash_field(nested_k, nested_v)
            out[k] = d

        return out

    # noinspection PyMethodMayBeStatic
    def _hash_field(self, field, value):
        if isinstance(value, (int, float, bool)):
            # Support hashing ints, floats and bools
            # for search filters
            value = str(value)

        try:
            return hashlib.sha512(value.encode("utf-8")).hexdigest()
        except TypeError:
            raise ValueError(
                f"Cannot hash field '{field}' as it is an "
                f"unsupported type {value.__class__.__name__}"
            )
