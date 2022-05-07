from typing import runtime_checkable, Protocol, Union, List, Dict, TypeVar

T = TypeVar("T")


@runtime_checkable
class ComparisonT(Protocol):
    """A protocol for all Comparison classes to follow."""

    def __init__(self, field: str, value: Union[List[T], T]):
        ...

    def __repr__(self):
        ...

    def build(self) -> Dict:
        """Return this instance as a usable Mongo filter."""
        ...
