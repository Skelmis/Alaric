from typing import Dict, Union


class Exists:
    """
    Returns all documents that contain this field.

    This class can be used in conjunction with :py:class:`~alaric.meta.NEGATE`

    Parameters
    ----------
    field: str
        The field to check in.


    Lets match all documents where the field ``prefix`` exists

    .. code-block:: python

        from alaric import AQ
        from alaric.comparison import EXISTS

        query = AQ(EXISTS("prefix"))
    """

    def __init__(self, field: str):
        self.field: str = field
        self._val: bool = True

    def __repr__(self):
        return f"EXISTS(field='{self.field}')"

    def build(self) -> Dict[str, Dict[str, Union[int, str, float, bytes]]]:
        """Return this instance as a usable Mongo filter."""
        return {self.field: {"$exists": self._val}}
