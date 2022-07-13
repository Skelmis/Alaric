from typing import Dict, Union

from alaric.types import ObjectId


class EQ:
    """
    Asserts the provided field is equal to the provided value.

    Parameters
    ----------
    field: str
        The field to check in.
    value: Union[int, str, float, bytes, dict, ObjectId]
        The value the field should equal.

    Notes
    -----
    This also works on matching items in arrays
    in an OR based matching approach.


    Lets match a document with an ``_id`` equal to ``1``

    .. code-block:: python

        from alaric import AQ
        from alaric.comparison import EQ

        query = AQ(EQ("_id", 1))
    """

    def __init__(
        self, field: str, value: Union[int, str, float, bytes, dict, ObjectId]
    ):
        self.field: str = field
        assert not isinstance(value, (list, tuple, set))
        self.value: Union[int, str, float, bytes, dict, ObjectId] = value
        self._operator = "$eq"

    def __repr__(self):
        return f"EQ(field='{self.field}', value={self.value})"

    def build(
        self,
    ) -> Dict[str, Dict[str, Union[int, str, float, bytes, dict, ObjectId]]]:
        """Return this instance as a usable Mongo filter."""
        return {self.field: {self._operator: self.value}}
