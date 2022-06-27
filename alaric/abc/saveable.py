from typing import runtime_checkable, Protocol, Dict


@runtime_checkable
class Saveable(Protocol):
    """Protocol for class based Queries."""

    def as_dict(self) -> Dict:
        """Returns this class represented as a dictionary."""
        ...
