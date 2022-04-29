from typing import Dict, Union


class EQ:
    """
    Asserts the provided field is equal to the provided value.

    Parameters
    ----------
    field: str
        The field to check in.
    value: Union[int, str, float, bytes]
        The value the field should equal.
    """

    def __init__(self, field: str, value: Union[int, str, float, bytes]):
        self.field: str = field
        assert not isinstance(value, (list, tuple, set))
        self.value: Union[int, str, float, bytes] = value

    def build(self) -> Dict[str, Dict[str, Union[int, str, float, bytes]]]:
        """Return this instance as a usable Mongo filter."""
        return {self.field: {"$eq": self.value}}
