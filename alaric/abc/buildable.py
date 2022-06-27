from typing import runtime_checkable, Protocol, Dict


@runtime_checkable
class Buildable(Protocol):
    """Protocol for class based Queries."""

    def build(self) -> Dict:
        """Return this instance as a usable Mongo filter."""
        ...
