import hashlib


def hash_field(field, value):
    """Hash a field with SHA512

    Parameters
    ----------
    field: str
        The name of the field your hashing
    value
        The value to hash

    Raises
    ------
    ValueError
        Unsupported type to hash
    """
    if isinstance(value, (int, float, bool)):
        # Support hashing ints, floats and bools
        # for search filters
        value = str(value)

    try:
        return hashlib.sha512(value.encode("utf-8")).hexdigest()
    except TypeError:
        raise ValueError(
            f"Cannot hash field '{field}' as it is an "
            f"unsupported type {value.__class__.__name__}"
        )
