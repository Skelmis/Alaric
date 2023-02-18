from alaric.encryption import Base


class HashedFields(Base):
    """A list of fields which should be hashed when encountered.

    Due to the nature of hashing, this is a one way operation
    and is only done when sending items to Mongo.

    .. note::

        Take care not to pass the hashed output back
        to a method which sends data to Mongo as it will
        result in it being re-hashed.

        If this is the case, tell the document method to
        ignore processing the field.


    .. code-block:: python
        :linenos:

        from alaric.encryption import HashedFields

        HashedFields("guild_id", "test")
    """
