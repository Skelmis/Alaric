from typing import Dict, Union


class LT:
    """
    Asserts the provided field is less to the provided value.

    This class can be used in conjunction with :py:class:`~alaric.meta.NEGATE`

    Parameters
    ----------
    field: str
        The field to check in.
    value: Union[int, str, float, bytes, dict]
        The value the field should be less than.


    Lets match all documents where the field ``counter``
    is less then 5.

    .. code-block:: python

        from alaric import AQ
        from alaric.comparison import LT

        query = AQ(LT("counter", 5))
    """

    def __init__(self, field: str, value: Union[int, str, float, bytes]):
        self.field: str = field
        assert not isinstance(value, (list, tuple, set))
        self.value: Union[int, str, float, bytes] = value

    def __repr__(self):
        return f"LT(field='{self.field}', value={self.value})"

    def build(self) -> Dict[str, Dict[str, Union[int, str, float, bytes]]]:
        """Return this instance as a usable Mongo filter."""
        return {self.field: {"$lt": self.value}}
