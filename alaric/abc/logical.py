from __future__ import annotations

from typing import (
    runtime_checkable,
    Protocol,
    TYPE_CHECKING,
    List,
    Dict,
    Union,
)

if TYPE_CHECKING:
    from alaric.abc import ComparisonT


@runtime_checkable
class LogicalT(Protocol):
    """A protocol for all Logical classes to follow."""

    def __init__(
        self,
        *comparisons: Union[
            Union[ComparisonT, LogicalT],
            List[Union[ComparisonT, LogicalT]],
        ]
    ):
        ...

    def __repr__(self):
        ...

    def build(self) -> Dict[str, List[Dict]]:
        """Return this instance as a usable Mongo filter."""
        ...
