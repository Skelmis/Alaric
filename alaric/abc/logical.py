from __future__ import annotations

from typing import runtime_checkable, Protocol, TYPE_CHECKING, List, Dict, Literal

if TYPE_CHECKING:
    from alaric.abc import ComparisonT


@runtime_checkable
class LogicalT(Protocol):
    def __init__(self, comparable_one: ComparisonT, comparable_two: ComparisonT):
        ...

    def build(self) -> Dict[str, List[Dict]]:
        ...
