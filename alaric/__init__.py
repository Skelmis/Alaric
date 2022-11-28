import logging
from collections import namedtuple

from .advanced_query import AQ
from .document import Document

Ascending = 1
Descending = -1

__all__ = ("AQ", "Document", "Ascending", "Descending")
__version__ = "1.1.4"
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(major=1, minor=1, micro=4, releaselevel="final", serial=0)
logging.getLogger(__name__).addHandler(logging.NullHandler())
