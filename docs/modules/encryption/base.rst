Encryption at rest
==================

Data security is a big thing these days and its especially prevalent
in my life as I work in Cyber Security, however, I am also not a
massive business who can afford to pay for Mongo enterprise to support
encryption at rest so this is my next best thing.

The new document subclass supports both encrypting fields with AES
and hashing fields with SHA512.

Database design impacts
***********************

Q: I want to encrypt my fields but need to be able to do query filtering on them?
A:
I suggest mirroring the fields, one hashed and one encrypted.

You can run filters against the hashed field as hashes don't change, and
when you need to gain access to that data you can fetch it via the encrypted field.


Q: I want to hash my ``XXX`` field, but I also need to know the value sometimes?
A:
See above.

Q: I encrypted my data using a generated key and lost it. Help!
A:
Your data is gone if you lose your key.

The whole point of encrypting fields is so people without
the key are unable to decrypt the data. When you lose the key,
you also fall into this group of people.

Q: How do I query a hashed field if I don't know the hash?
A:
Created your query as per usual, just wrap your comparison
object in ``HQF(...)`` and Alaric will handle it for you.

.. code-block:: python

        from alaric import AQ
        from alaric.comparison import EQ
        from alaric.encryption import HQF

        query = AQ(HQF(EQ("_id", 1)))


Class Reference
***************

.. currentmodule:: alaric

.. autoclass:: EncryptedDocument
    :members:
    :undoc-members:
    :special-members: __init__
