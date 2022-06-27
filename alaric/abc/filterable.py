from typing import runtime_checkable, Protocol, Dict


@runtime_checkable
class Filterable(Protocol):
    """Protocol for class based Queries."""

    def as_filter(self) -> Dict:
        """Returns a dictionary that represents
        a filter required to return this object.
        """
        ...
