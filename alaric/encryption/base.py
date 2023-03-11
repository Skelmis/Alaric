from typing import Set


class Base:
    def __init__(self, *fields: str):
        self.fields: Set = set(fields)

    def __contains__(self, item):
        return item in self.fields

    def __repr__(self):
        return f"{self.__class__.__name__}({','.join(self.fields)})"

    def __iter__(self):
        return iter(self.fields)
