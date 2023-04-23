import logging
from collections import namedtuple

from .advanced_query import AQ
from .document import Document
from .cursor import Cursor
from .encrypted_document import EncryptedDocument

Ascending = 1
Descending = -1

__all__ = (
    "AQ",
    "Document",
    "Ascending",
    "Descending",
    "Cursor",
    "EncryptedDocument",
    "util",
)
__version__ = "1.3.3"
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(major=1, minor=3, micro=3, releaselevel="final", serial=0)
logging.getLogger(__name__).addHandler(logging.NullHandler())
