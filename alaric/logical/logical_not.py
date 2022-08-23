from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Union

if TYPE_CHECKING:
    from alaric.abc import ComparisonT, LogicalT, Buildable


class NOT:
    """Invert the effect of a query expression.

    This back-links to `here <https://www.mongodb.com/docs/manual/reference/operator/query/not/#mongodb-query-op.-not>`_


    Lets find all items where my ``gamer_tag`` does NOT match ``Skelmis``

    .. code-block:: python
        :linenos:

        from alaric import AQ
        from alaric.logical import NOT
        from alaric.comparison import EQ

        query = AQ(NOT(EQ("gamer_tag", "Skelmis")))
    """

    def __init__(
        self,
        *comparisons: Union[
            Union[ComparisonT, LogicalT, Buildable],
            List[Union[ComparisonT, LogicalT, Buildable]],
        ],
    ):
        self.comparisons: List[Union[ComparisonT, LogicalT]] = list(comparisons)

    def __repr__(self):
        return f"NOT(comparisons={self.comparisons})"

    def build(self) -> Dict[str, List[Dict]]:
        """Return this instance as a usable Mongo filter."""
        comparisons: List[Dict] = [c.build() for c in self.comparisons]
        return {"$not": comparisons}
