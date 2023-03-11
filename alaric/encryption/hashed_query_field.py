from __future__ import annotations

import hashlib
from typing import Union, Dict

from alaric import util
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
                d[nested_k] = util.hash_field(nested_k, nested_v)
            out[k] = d

        return out
