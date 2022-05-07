from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Union

if TYPE_CHECKING:
    from alaric.abc import ComparisonT, LogicalT


class NOT:
    """Invert the effect of a query expression.

    This back-links to `here <https://www.mongodb.com/docs/manual/reference/operator/query/not/#mongodb-query-op.-not>`
    """

    def __init__(
        self,
        *comparisons: Union[
            Union[ComparisonT, LogicalT],
            List[Union[ComparisonT, LogicalT]],
        ],
    ):
        self.comparisons: List[Union[ComparisonT, LogicalT]] = list(comparisons)

    def __repr__(self):
        return f"NOT(comparisons={self.comparisons})"

    def build(self) -> Dict[str, List[Dict]]:
        """Return this instance as a usable Mongo filter."""
        comparisons: List[Dict] = [c.build() for c in self.comparisons]
        return {"$not": comparisons}
