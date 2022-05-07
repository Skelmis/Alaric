from typing import runtime_checkable, Protocol, Dict


@runtime_checkable
class BuildAble(Protocol):
    def build(self) -> Dict:
        ...
