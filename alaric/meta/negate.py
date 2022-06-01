from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from alaric.comparison import IN, GT, LT
from alaric.comparison.comparison_exists import EXISTS

if TYPE_CHECKING:
    from alaric.abc import ComparisonT


class NEGATE:
    """
    Negate a given option, I.e. Do the opposite.

    Supported operands:

    * EXISTS
    * IN
    """

    def __init__(self, comparison: ComparisonT):
        self.comparison: ComparisonT = comparison

    def __repr__(self):
        return f"NEGATE({self.comparison})"

    def build(self) -> Dict:
        if isinstance(self.comparison, EXISTS):
            self.comparison._val = False
            return self.comparison.build()

        elif isinstance(self.comparison, IN):
            self.comparison._operator = "$nin"
            return self.comparison.build()

        elif isinstance(self.comparison, GT):
            raise RuntimeError("Cannot negate GT, use LT instead.")

        elif isinstance(self.comparison, LT):
            raise RuntimeError("Cannot negate LT, use GT instead.")

        raise RuntimeError("Invalid wrapped comparison.")
