from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Union

if TYPE_CHECKING:
    from alaric.abc import ComparisonT, LogicalT, Buildable


class OR:
    """Conduct a logical OR between all items passed to the constructor.

    Lets build a check using a simple OR which will return
    all results the field ``my_field`` is either ``True``
    OR a number in the list ``[1, 2, 3, 7, 8, 9]``

    .. code-block:: python
        :linenos:

        from alaric import AQ
        from alaric.logical import OR
        from alaric.comparison import EQ, IN

        query = AQ(OR(EQ("my_field", True), IN("my_field", [1, 2, 3, 7, 8, 9])))
    """

    def __init__(
        self,
        *comparisons: Union[
            Union[ComparisonT, LogicalT, Buildable],
            List[Union[ComparisonT, LogicalT, Buildable]],
        ],
    ):
        self.comparisons: List[Union[ComparisonT, LogicalT, Buildable]] = list(
            comparisons
        )

    def __repr__(self):
        return f"OR(comparisons={self.comparisons})"

    def build(self) -> Dict[str, List[Dict]]:
        """Return this instance as a usable Mongo filter."""
        comparisons: List[Dict] = [c.build() for c in self.comparisons]
        return {"$or": comparisons}
