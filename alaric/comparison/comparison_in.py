from typing import Dict, Union


class IN:
    """
    Asserts the provided field is within the provided values.

    This class can be used in conjunction with :py:class:`NEGATE`

    Parameters
    ----------
    field: str
        The field to check in.
    value: Union[list, tuple, set]
        A iterable of values that field should be in.
    """

    def __init__(self, field: str, value: Union[list, tuple, set]):
        self.field: str = field
        assert isinstance(value, (list, tuple, set))
        self.value: Union[list, tuple, set] = value

        self._operator = "$in"

    def __repr__(self):
        return f"IN(field='{self.field}', value={self.value})"

    def build(self) -> Dict[str, Dict[str, Union[list, tuple, set]]]:
        """Return this instance as a usable Mongo filter."""
        return {self.field: {self._operator: self.value}}
