from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Union

if TYPE_CHECKING:
    from alaric.abc import ComparisonT, LogicalT, Buildable


class AND:
    """Conduct a logical AND between all items passed to the constructor.


    Lets build a query which returns all results where the field ``discord``
    is equal to ``Skelmis#9135`` and ``gamer_tag`` is equal to ``Skelmis``

    .. code-block:: python
        :linenos:

        from alaric import AQ
        from alaric.logical import AND
        from alaric.comparison import EQ

        query = AQ(AND(EQ("discord", "Skelmis#9135"), EQ("gamer_tag", "Skelmis")))
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
        return f"AND(comparisons={self.comparisons})"

    def build(self) -> Dict[str, List[Dict]]:
        """Return this instance as a usable Mongo filter."""
        comparisons: List[Dict] = [c.build() for c in self.comparisons]
        return {"$and": comparisons}
