from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Union

if TYPE_CHECKING:
    from alaric.abc import ComparisonT, LogicalT


class AND:
    def __init__(
        self,
        *comparisons: Union[
            Union[ComparisonT, LogicalT],
            List[Union[ComparisonT, LogicalT]],
        ]
    ):
        self.comparisons: List[Union[ComparisonT, LogicalT]] = list(comparisons)

    def build(self) -> Dict[str, List[Dict]]:
        """Return this instance as a usable Mongo filter."""
        comparisons: List[Dict] = [c.build() for c in self.comparisons]
        return {"$and": comparisons}
