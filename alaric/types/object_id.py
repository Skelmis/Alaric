from typing import Union

from bson import ObjectId as OID


class ObjectId(OID):
    """A thin wrapper over bson.ObjectId for usage within Alaric"""

    def __init__(self, object_id: Union[str, "ObjectId", bytes]):
        super().__init__(object_id)

    @property
    def object_id(self) -> Union[str, "ObjectId", bytes]:
        return self.__id
