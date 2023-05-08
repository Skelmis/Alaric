from alaric.encryption import Base


class AutomaticHashedFields(Base):
    """A list of fields which should have a hashed field
    created automatically in the background but without access to the user.

    I.e. Alaric when told to automatically hash the field ``guild_id``
    will look at incoming data, create an extra field called ``guild_id_hashed``
    and add it to the database. Whenever you fetch data from the database,
    Alaric will remove this field so you never see it.

    If you want to use this field in your code,
    use :py:class:`alaric.encryption.HashedFields` instead.

    .. code-block:: python
        :linenos:

        from alaric.encryption import AutomaticHashedFields

        AutomaticHashedFields("guild_id", "test")

    .. note::
        You can use this in conjunction with an encrypted field to
        have a hash representing the unencrypted data.
    """
