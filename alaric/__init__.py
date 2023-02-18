import logging
from collections import namedtuple

from .advanced_query import AQ
from .document import Document
from .cursor import Cursor
from .encrypted_document import EncryptedDocument

Ascending = 1
Descending = -1

__all__ = ("AQ", "Document", "Ascending", "Descending", "Cursor", "EncryptedDocument")
__version__ = "1.2.0"
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(major=1, minor=2, micro=0, releaselevel="final", serial=0)
logging.getLogger(__name__).addHandler(logging.NullHandler())
