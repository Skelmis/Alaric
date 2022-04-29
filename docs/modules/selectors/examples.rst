Example Usage
=============

Some example query building for advanced usage.
You will pass the ``query`` variable to ``find`` or ``find_many``.

Or usage
--------

Lets build a check using a simple OR which will return
all results that are either ``True`` OR the numbers ``1,2,3,7,8,9``

.. code-block:: python
    :linenos:

    from alaric import AQ
    from alaric.logical import OR
    from alaric.comparison import EQ, IN

    query = AQ(OR(EQ("my_field", True), IN("my_field", [1, 2, 3, 7, 8, 9])))


And usage
---------

Lets build a query which returns all results where the field ``discord``
is equal to ``Skelmis#9135`` and ``gamer_tag`` is equal to ``Skelmis``

.. code-block:: python
    :linenos:

    from alaric import AQ
    from alaric.logical import AND
    from alaric.comparison import EQ

    query = AQ(AND(EQ("discord", "Skelmis#9135"), EQ("gamer_tag", "Skelmis")))
