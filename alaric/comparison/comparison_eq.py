from typing import Dict, Union


class EQ:
    """
    Asserts the provided field is equal to the provided value.

    Parameters
    ----------
    field: str
        The field to check in.
    value: Union[int, str, float, bytes, dict]
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

    def __init__(self, field: str, value: Union[int, str, float, bytes, dict]):
        self.field: str = field
        assert not isinstance(value, (list, tuple, set))
        self.value: Union[int, str, float, bytes, dict] = value

    def __repr__(self):
        return f"EQ(field='{self.field}', value={self.value})"

    def build(self) -> Dict[str, Dict[str, Union[int, str, float, bytes, dict]]]:
        """Return this instance as a usable Mongo filter."""
        return {self.field: {"$eq": self.value}}
