from typing import Dict


class Regex:
    """
    Provides an interface for fetching data based on a given regex.

    Let's match all documents where the field ``title``
    contains the word "Blade"

    .. code-block:: python

        from alaric import AQ
        from alaric.comparison import Regex

        query = AQ(Regex("title", "Blade"))

    For further options see:
    https://www.mongodb.com/docs/manual/reference/operator/query/regex/
    """

    def __init__(
        self,
        field: str,
        regex: str,
        *,
        case_insensitive: bool = False,
        other_options: str = "",
    ):
        self.field: str = field
        self.regex = regex
        self.case_insensitive = case_insensitive
        self.options = other_options
        if case_insensitive:
            self.options += "i"

    def __repr__(self):
        return f"Regex({self.regex=}, {self.options=})"

    def build(self) -> Dict[str, Dict[str, str]]:
        """Return this instance as a usable Mongo filter."""
        return {self.field: {"$regex": self.regex, "$options": self.options}}
