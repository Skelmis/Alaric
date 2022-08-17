Why Alaric
==========

TL;DR
-----

* Comes with typing and autocomplete support built in
* Support for class based structures, no more ``data["_id"]`` or ``find_one({...})``
* Simplistic advanced querying support
* Convenience methods for everyday operations
* Built on motor, so if Alaric can't do it your not left in the lurch

----------

For the sake of all examples, ``document`` will refer to an instance of :py:class:`~alaric.Document`
while ``collection`` will refer to an instance of ``AsyncIOMotorCollection``

Basic Queries
-------------

At a basic level, :py:class:`~alaric.Document` is used fairly similar to ``AsyncIOMotorCollection``
in that your basic queries cross over, for example:

.. code-block:: python
    :linenos:

    # These are the same
    r_1 = await collection.find_one({"_id": 1234})
    r_2 = await document.find({"_id": 1234})

At its core, all methods accept the dictionaries you are used to.
Where this is not true, your type checker will notify you.

Automatic Class Conversion
--------------------------

Lets imagine our data is structured like this:

.. code-block::

    {
        "_id": int,
        "prefix:" str,
        "activated_premium": bool,
    }

With motor the following would be a fairly standard interaction.

.. code-block:: python
    :linenos:

    data = await collection.find_one({"_id": 1234})
    prefix = data["prefix"]
    ...
    if data["activated_premium"]:
        ...

Raw dictionaries, no autocomplete, frankly yuck.

Now, by default Alaric also returns raw dictionaries, however, the following
is also valid syntax and how I personally like to use the package.

.. code-block:: python
    :linenos:

    class Guild:
        def __init__(self, _id, prefix, activated_premium):
            self._id: int = _id
            self.prefix: str = prefix
            self.activated_premium: bool = activated_premium

    document = Document(..., converter=Guild)
    guild: Guild = await document.find({"_id": 1234})
    prefix = guild.prefix
    ...
    if guild.activated_premium:
        ...

.. note::

    Due to how Alaric is built, your ``__init__`` must accept all arguments from
    your returned data. If there is extra, say an unwanted ``_id`` I recommend
    just adding ``**kwargs`` and not using them in the method itself.


Fully utilizing class support
*****************************

In the previous example you still have to convert it to a dictionary
whenever you wanted to insert / update / filter. Lets change that.

Alaric exposes two protocol methods, which if implemented will be used.

These are:

* ``as_filter``
    Treat the dictionary returned from this as a filter for a query.

    I.e. ``as_filter`` would return ``{"_id": 1234}``
* ``as_dict``
    Treat the dictionary returned from this as a full representation
    of the current object instance.

    I.e. ``as_dict`` would return ``{"_id": 1234, "prefix": "!", "activated_premium": True}``

Lets see them in action.

.. code-block:: python
    :linenos:

    from typing import Dict

    class Guild:
        def __init__(self, _id, prefix, activated_premium):
            self._id: int = _id
            self.prefix: str = prefix
            self.activated_premium: bool = activated_premium

        def as_filter(self) -> Dict:
            return {"_id": self._id}

        def as_dict(self) -> Dict:
            return {
                "_id": self._id,
                "prefix": self.prefix,
                "activated_premium": self.activated_premium,
            }

    document = Document(..., converter=Guild)
    guild: Guild = Guild(5678, "py.", False)
    await document.insert(guild)

    # Alternatively
    guild: Guild = await document.find({"_id": 1234})
    guild.prefix = "?"
    await document.upsert(guild, guild)

.. note::

    For the last example you should actually use :py:meth:`alaric.Document.change_field_to`


Conditional Class Returns
*************************

In a situation where you don't want you returned data to be converted to your class?

Simply pass ``try_convert=False`` to the method.


Advanced Querying
-----------------

This is a hidden gem, but MongoDB actually supports some extremely powerful queries.
The issue however is the relevant dictionaries get big, quick.

Using our prior data structure, lets run a query to return all guilds
that have the prefix ``?``.

.. code-block:: python

    await document.find({"prefix": "?"})

Simple right?

How about all guilds where the prefix is either ``!`` or ``?``?

Now, the raw query for this would look something like this.

.. code-block:: python

    await document.find({'prefix': {'$in': ['!', '?']}})

But with Alaric you can make the same query like this.

.. code-block:: python

    from alaric import AQ
    from alaric.comparison import IN

    await document.find(AQ(IN("prefix", ["!", "?"])))

I know what I'd prefer.

----------

But lets make it even more complex!

Lets query for all the guilds that have activated premium, and have
a prefix as either ``!`` or ``?``.

Now, the raw query for this would look something like this.

.. code-block:: python

    await document.find(
        {
            "$and": [
                {"prefix": {"$in": ["!", "?"]}},
                {"activated_premium": {"$eq": True}},
            ]
        }
    )

But with Alaric you can make the same query like this.

.. code-block:: python

    from alaric import AQ
    from alaric.logical import AND
    from alaric.comparison import EQ, IN

    await document.find(AQ(AND(IN("prefix", ["!", "?"]), EQ("activated_premium", True))))

And this is only the tip of the iceberg, there are so many types of queries you can do.