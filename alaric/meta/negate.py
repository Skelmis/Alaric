from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict

from alaric.comparison import IN, GT, LT, EQ
from alaric.comparison.comparison_exists import Exists

if TYPE_CHECKING:
    from alaric.abc import ComparisonT

log = logging.getLogger(__name__)


class Negate:
    """
    Negate a given option, I.e. Do the opposite.

    Supported operands:

    * :py:class:`~alaric.comparison.Exists`
    * :py:class:`~alaric.comparison.IN`
    * :py:class:`~alaric.comparison.GT`
    * :py:class:`~alaric.comparison.LT`
    * :py:class:`~alaric.comparison.EQ`


    Lets get all documents *without* a field called ``prefix``

    .. code-block:: python
        :linenos:

        from alaric.comparison import Exists
        from alaric.meta import Negate
        from alaric import AQ

        query = AQ(Negate(Exists("prefix")))
    """

    def __init__(self, comparison: ComparisonT):
        self.comparison: ComparisonT = comparison

    def __repr__(self):
        return f"NEGATE({self.comparison})"

    def build(self) -> Dict:
        """Returns a mongo usable filter for the negated option."""
        if isinstance(self.comparison, Exists):
            self.comparison._val = False
            return self.comparison.build()

        elif isinstance(self.comparison, IN):
            self.comparison._operator = "$nin"
            return self.comparison.build()

        elif isinstance(self.comparison, GT):
            log.debug("Use LT rather then negating GT")
            self.comparison = LT(self.comparison.field, self.comparison.value)

        elif isinstance(self.comparison, LT):
            log.debug("Use GT rather then negating LT")
            self.comparison = GT(self.comparison.field, self.comparison.value)

        elif isinstance(self.comparison, EQ):
            self.comparison._operator = "$ne"
            return self.comparison.build()

        raise RuntimeError("Invalid wrapped comparison.")
