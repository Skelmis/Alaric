from __future__ import annotations

import logging
from typing import Dict


log = logging.getLogger(__name__)


class All:
    """
    Return all documents in the collection.

    .. code-block:: python
        :linenos:

        from alaric.meta import All

        query = AQ(All())
    """

    def __repr__(self):
        return f"ALL()"

    def build(self) -> Dict:
        return {}
