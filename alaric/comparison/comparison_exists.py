from typing import Dict, Union


class EXISTS:
    """
    Returns all documents that contain this field.

    Parameters
    ----------
    field: str
        The field to check in.
    """

    def __init__(self, field: str):
        self.field: str = field
        self._val: bool = True

    def __repr__(self):
        return f"EXISTS(field='{self.field}')"

    def build(self) -> Dict[str, Dict[str, Union[int, str, float, bytes]]]:
        """Return this instance as a usable Mongo filter."""
        return {self.field: {"$exists": self._val}}