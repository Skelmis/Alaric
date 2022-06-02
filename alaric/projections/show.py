from typing import Any, Dict, List


class SHOW:
    """Show this field in the returned data."""

    def __init__(self, *fields: Any):
        self.fields: List[Any] = list(fields)

    def __repr__(self):
        return f"SHOW({self.fields})"

    def build(self) -> Dict:
        return {field: 1 for field in self.fields}
