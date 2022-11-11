class Converter:
    def __init__(self, _id, value=None):
        self._id = _id
        self.value = value

    @property
    def id(self):
        return self._id

    def as_filter(self):
        return {"_id": self._id}

    def as_dict(self):
        return {"_id": self._id, "value": self.value}
