from __future__ import annotations

from typing import Dict, List, Union, cast

from alaric.abc import Buildable
from alaric.projections import Show, Hide


class Projection:
    """Specify that only the given fields should be returned from the query.

    .. code-block:: python
        :linenos:

        # Assuming the data structure
        # {"_id": 1234, "prefix": "!", "has_premium": False}
        data: dict = await Document.find(
            {"_id": "my_id"}, projections=Projection(Show("prefix"))
        )
        print(data)
        # Will print {"prefix": "!"}
    """

    def __init__(self, *fields: Union[Show, Hide]):
        self.fields: List[Union[Show, Hide]] = list(fields)

    def __repr__(self):
        return f"Projection({self.fields})"

    def build(self) -> Dict:
        fields: Dict = {}
        for field in self.fields:
            field = cast(Buildable, field)
            fields = {**fields, **field.build()}

        if "_id" not in fields:
            # Hide unless asked
            fields["_id"] = 0

        return fields
