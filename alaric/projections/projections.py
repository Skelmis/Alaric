from __future__ import annotations

from typing import Dict, List, Union, cast

from alaric.abc import Buildable
from alaric.projections import SHOW, HIDE


class PROJECTION:
    """Specify that only the given fields should be returned."""

    def __init__(self, *fields: Union[SHOW, HIDE]):
        self.fields: List[Union[SHOW, HIDE]] = list(fields)

    def __repr__(self):
        return f"PROJECTION({self.fields})"

    def build(self) -> Dict:
        fields: Dict = {}
        for field in self.fields:
            field = cast(Buildable, field)
            fields = {**fields, **field.build()}

        if "_id" not in fields:
            # Hide unless asked
            fields["_id"] = 0

        return fields
