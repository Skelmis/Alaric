from typing import runtime_checkable, Protocol, Union, List, Dict, TypeVar

T = TypeVar("T")


@runtime_checkable
class ComparisonT(Protocol):
    def __init__(self, field: str, value: Union[List[T], T]):
        ...

    def build(self) -> Dict:
        ...
