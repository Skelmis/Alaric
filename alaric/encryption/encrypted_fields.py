from alaric.encryption import Base


class EncryptedFields(Base):
    """A list of fields which should be encrypted when encountered.

    .. code-block:: python
        :linenos:

        from alaric.encryption import EncryptedFields

        EncryptedFields("guild_id", "test")
    """
