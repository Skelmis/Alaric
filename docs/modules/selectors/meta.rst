Meta Classes
============

Extra classes which don't fit into a given category

All of these classes are importable from ``alaric.meta``

.. currentmodule:: alaric.meta

Negate
------

.. autoclass:: NEGATE
    :members:
    :undoc-members:

.. code-block:: python
    :linenos:

    from alaric.comparison import EXISTS
    from alaric.meta import NEGATE
    from alaric import AQ

    query = AQ(NEGATE(EXISTS("field")))



