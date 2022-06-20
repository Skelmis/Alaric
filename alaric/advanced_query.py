from typing import Union, List, Dict

from alaric.abc import ComparisonT, LogicalT


class AQ:
    """
    A container representing an advanced query.

    Parameters
    ----------
    item: Union[ComparisonT, LogicalT]]
        The parent item we wish to build upon.


    .. code-block:: python

        from alaric import AQ
        from alaric.logical import AND
        from alaric.comparison import EQ, EXISTS

        query = AQ(AND(EQ("id", 1), EXISTS("prefix")))
    """

    def __init__(
        self,
        item: Union[
            ComparisonT,
            LogicalT,
        ],
    ):
        self._item: Union[ComparisonT, LogicalT] = item

    def build(self) -> Dict:
        """Return this AQ as a usable Mongo filter."""
        return self._item.build()
