from typing import TypeVar, Dict

T = TypeVar("T", int, str, float, bytes)


class EQ:
    def __init__(self, field: str, value: T):
        assert not isinstance(value, (list, tuple, set))
        self.field: str = field
        self.value: T = value

    def build(self) -> Dict[str, Dict[str, T]]:
        return {self.field: {"$eq": self.value}}
