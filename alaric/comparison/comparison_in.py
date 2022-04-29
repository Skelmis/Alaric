from typing import TypeVar, Dict

T = TypeVar("T", list, tuple, set)


class IN:
    def __init__(self, field: str, value: T):
        assert isinstance(value, (list, tuple, set))
        self.field: str = field
        self.value: T = value

    def build(self) -> Dict[str, Dict[str, T]]:
        return {self.field: {"$in": self.value}}
