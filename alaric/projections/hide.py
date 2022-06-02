from typing import Any, Dict, List


class HIDE:
    """Hide this field in the returned data."""

    def __init__(self, *fields: Any):
        self.fields: List[Any] = list(fields)

    def __repr__(self):
        return f"HIDE({self.fields})"

    def build(self) -> Dict:
        return {field: 0 for field in self.fields}
