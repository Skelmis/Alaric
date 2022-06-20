from typing import Dict, Union


class GT:
    """
    Asserts the provided field is greater to the provided value.

    This class can be used in conjunction with :py:class:`~alaric.meta.NEGATE`

    Parameters
    ----------
    field: str
        The field to check in.
    value: Union[int, str, float, bytes, dict]
        The value the field should be greater than.


    Lets match all documents where the field ``counter``
    is greater then 5.

    .. code-block:: python

        from alaric import AQ
        from alaric.comparison import GT

        query = AQ(GT("counter", 5))
    """

    def __init__(self, field: str, value: Union[int, str, float, bytes]):
        self.field: str = field
        assert not isinstance(value, (list, tuple, set))
        self.value: Union[int, str, float, bytes] = value

    def __repr__(self):
        return f"GT(field='{self.field}', value={self.value})"

    def build(self) -> Dict[str, Dict[str, Union[int, str, float, bytes]]]:
        """Return this instance as a usable Mongo filter."""
        return {self.field: {"$gt": self.value}}
